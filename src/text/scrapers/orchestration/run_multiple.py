"""
Pacific Observatory - Multi-Scraper Runner

This module contains all the logic for running multiple newspaper scrapers
in parallel, with intelligent handling of multi-country newspapers.
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

# Import discovery functions from dedicated module
from text.scrapers.orchestration.discovery import discover_configs, group_by_newspaper
from text.scrapers.orchestration.utils import create_progress_display


def run_scraper_subprocess(
    config: Dict[str, str],
    log_dir: Path,
    project_root: Path,
    dry_run: bool = False,
    urls_from_scratch: bool = True,
) -> Optional[subprocess.Popen]:
    """
    Run a single scraper as a subprocess with nohup.
    
    Args:
        config: Configuration dictionary with 'country', 'newspaper', 'config_path'
        log_dir: Base directory for logs
        project_root: Project root directory
        dry_run: If True, print command without executing
        urls_from_scratch: Whether to discover URLs from scratch (True) or load from urls.csv (False)
    
    Returns:
        Popen object if started, None if dry_run or error
    """
    country = config["country"]
    newspaper = config["newspaper"]
    
    # Create log directory structure: logs/{country}/{newspaper}/
    log_subdir = log_dir / country / newspaper
    log_subdir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_subdir / f"{timestamp}.log"
    
    # Build command
    # Use poetry run if available, otherwise direct python
    cmd = [
        "poetry", "run", "python",
        str(project_root / "src" / "text" / "scrapers" / "orchestration" / "main.py"),
        newspaper,
        "--update",
        "--urls-from-scratch", str(urls_from_scratch),
    ]
    
    if dry_run:
        print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
        print(f"          Log file: {log_file}")
        return None
    
    # Open log file for writing
    log_handle = open(log_file, "w")
    
    # Start process with nohup-like behavior
    # Use subprocess.Popen with stdout/stderr redirected to log file
    try:
        process = subprocess.Popen(
            cmd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            cwd=str(project_root),
            start_new_session=True,  # Detach from parent session (nohup-like)
        )
        
        # Store metadata on the process object for later reference
        process.log_file = log_file
        process.country = country
        process.newspaper = newspaper
        process.log_handle = log_handle
        
        return process
    
    except Exception as e:
        print(f"❌ Failed to start {country}/{newspaper}: {e}")
        log_handle.close()
        return None


def monitor_processes(
    processes: List[subprocess.Popen],
    check_interval: float = 2.0,
    use_progress: bool = True,
) -> List[Dict[str, any]]:
    """
    Monitor running processes and report when they complete.
    
    Args:
        processes: List of Popen objects to monitor
        check_interval: Seconds between status checks
        use_progress: Whether to use Rich progress display
    
    Returns:
        List of result dictionaries with status information
    """
    results = []
    remaining = list(processes)
    
    if not use_progress:
        # Legacy mode: simple print statements
        print(f"\n🔄 Monitoring {len(processes)} scraper(s)...\n")
        
        while remaining:
            for process in remaining[:]:
                retcode = process.poll()
                
                if retcode is not None:
                    country = process.country
                    newspaper = process.newspaper
                    log_file = process.log_file
                    
                    if hasattr(process, 'log_handle'):
                        process.log_handle.close()
                    
                    status = parse_log_status(log_file, retcode)
                    
                    result = {
                        "country": country,
                        "newspaper": newspaper,
                        "log_file": log_file,
                        "exit_code": retcode,
                        "status": status,
                    }
                    results.append(result)
                    
                    status_icon = {
                        "success": "✅",
                        "warning": "⚠️",
                        "failed": "❌",
                    }.get(status, "❓")
                    
                    print(f"{status_icon} {country}/{newspaper} completed ({status})")
                    
                    remaining.remove(process)
            
            if remaining:
                time.sleep(check_interval)
        
        return results
    
    # Rich progress mode
    progress, console = create_progress_display()
    
    # Create task for each process
    task_map = {}  # process -> task_id
    
    with progress:
        for process in processes:
            task_id = progress.add_task(
                "[yellow]Running...",
                country=process.country,
                newspaper=process.newspaper,
                total=100,
                completed=0,
            )
            task_map[process] = task_id
        
        # Monitor processes
        while remaining:
            for process in remaining[:]:
                task_id = task_map[process]
                retcode = process.poll()
                
                if retcode is not None:
                    # Process finished
                    country = process.country
                    newspaper = process.newspaper
                    log_file = process.log_file
                    
                    if hasattr(process, 'log_handle'):
                        process.log_handle.close()
                    
                    status = parse_log_status(log_file, retcode)
                    
                    result = {
                        "country": country,
                        "newspaper": newspaper,
                        "log_file": log_file,
                        "exit_code": retcode,
                        "status": status,
                    }
                    results.append(result)
                    
                    # Update progress with final status
                    if status == "success":
                        progress.update(task_id, description="[green]✅ Completed", completed=100)
                    elif status == "warning":
                        progress.update(task_id, description="[yellow]⚠️  Completed (warnings)", completed=100)
                    else:
                        progress.update(task_id, description="[red]❌ Failed", completed=100)
                    
                    remaining.remove(process)
                else:
                    # Still running - update progress bar
                    current = progress.tasks[task_id].completed
                    if current < 90:  # Keep it moving but never reach 100 until done
                        progress.update(task_id, completed=min(current + 2, 90))
            
            if remaining:
                time.sleep(check_interval)
    
    return results


def parse_log_status(log_file: Path, exit_code: int) -> str:
    """
    Parse log file to determine scraper status.
    
    Args:
        log_file: Path to log file
        exit_code: Process exit code
    
    Returns:
        Status string: 'success', 'warning', or 'failed'
    """
    # Failed if non-zero exit code
    if exit_code != 0:
        return "failed"
    
    # Check log content for warnings or errors
    try:
        if not log_file.exists():
            return "failed"
        
        log_content = log_file.read_text()
        
        # Look for warning indicators
        warning_indicators = [
            "WARNING",
            "Warning",
            "Exception",
            "Error:",
            "Failed URLs:",
        ]
        
        has_warnings = any(indicator in log_content for indicator in warning_indicators)
        
        # Look for success indicators
        success_indicators = [
            "Scraping completed successfully",
            "✅",
        ]
        
        has_success = any(indicator in log_content for indicator in success_indicators)
        
        if has_success and not has_warnings:
            return "success"
        elif has_success and has_warnings:
            return "warning"
        else:
            return "failed"
    
    except Exception:
        return "failed"


def summarize_results(results: List[Dict[str, any]]):
    """
    Print a compact summary table of scraper results.
    
    Args:
        results: List of result dictionaries from monitor_processes()
    """
    if not results:
        print("\nNo results to summarize.")
        return
    
    # Count statuses
    status_counts = defaultdict(int)
    for result in results:
        status_counts[result["status"]] += 1
    
    # Print header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "─" * 60)
    print(f"SCRAPER SUMMARY ({timestamp})")
    print("─" * 60)
    
    # Print each result
    for result in sorted(results, key=lambda x: (x["country"], x["newspaper"])):
        status_icon = {
            "success": "✅",
            "warning": "⚠️",
            "failed": "❌",
        }.get(result["status"], "❓")
        
        status_text = {
            "success": "Completed successfully",
            "warning": "Completed with warnings",
            "failed": "Failed (see log)",
        }.get(result["status"], "Unknown status")
        
        country = result["country"]
        newspaper = result["newspaper"]
        
        print(f"{status_icon} {country:20s} / {newspaper:20s} {status_text}")
    
    # Print totals
    print("─" * 60)
    total = len(results)
    success = status_counts.get("success", 0)
    warnings = status_counts.get("warning", 0)
    failed = status_counts.get("failed", 0)
    
    print(f"Total: {total} | Success: {success} | Warnings: {warnings} | Failed: {failed}")
    print("─" * 60)


def run_multi_country_group_sequential(
    group: List[Dict[str, str]],
    log_dir: Path,
    project_root: Path,
    dry_run: bool = False,
    urls_from_scratch: bool = True,
) -> List[Dict[str, any]]:
    """
    Run a multi-country newspaper group sequentially.
    
    This function runs all countries for a single newspaper sequentially
    to avoid rate limiting and blocking issues.
    
    Args:
        group: List of config dictionaries for the same newspaper across countries
        log_dir: Base directory for logs
        project_root: Project root directory
        dry_run: If True, print command without executing
        urls_from_scratch: Whether to discover URLs from scratch (True) or load from urls.csv (False)
    
    Returns:
        List of result dictionaries
    """
    newspaper_name = group[0]["newspaper"]
    print(f"\n   Group: {newspaper_name} ({len(group)} countries)")
    
    results = []
    for config in group:
        print(f"      Starting {config['country']}/{config['newspaper']}...")
        process = run_scraper_subprocess(config, log_dir, project_root, dry_run, urls_from_scratch)
        if process:
            # Wait for this scraper to complete before starting the next one
            group_results = monitor_processes([process])
            results.extend(group_results)
    
    return results


def run_all_scrapers(
    configs_dir: Path,
    project_root: Path,
    sequential: bool = False,
    dry_run: bool = False,
    urls_from_scratch: bool = True,
) -> bool:
    """
    Run all newspaper scrapers with intelligent parallel/sequential execution.
    
    Single-country newspapers run in parallel.
    Multi-country newspapers run sequentially in separate processes to avoid interference.
    
    Args:
        configs_dir: Path to the configs directory
        project_root: Project root directory
        sequential: If True, run all scrapers sequentially (for debugging)
        dry_run: If True, print what would be executed without running
        urls_from_scratch: Whether to discover URLs from scratch (True) or load from urls.csv (False)
    
    Returns:
        True if all scrapers succeeded, False if any failed
    """
    print("🌊 Pacific Observatory - Multi-Scraper Runner")
    print("=" * 60)
    
    # Discover all configurations
    print("\n🔍 Discovering configurations...")
    configs = discover_configs(configs_dir)
    
    if not configs:
        print("❌ No configurations found.")
        return False
    
    print(f"   Found {len(configs)} scraper configuration(s)")
    
    # Group by newspaper to handle multi-country cases
    single_country, multi_country = group_by_newspaper(configs)
    
    print(f"   - {len(single_country)} single-country newspapers")
    print(f"   - {len(multi_country)} multi-country newspaper groups")
    
    # Set up log directory
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    if dry_run:
        print("\n[DRY RUN MODE - No scrapers will actually run]\n")
    
    parallel_processes = []
    sequential_processes = []
    all_results = []
    
    # Run single-country newspapers (can run in parallel)
    if single_country:
        print(f"\n🚀 Starting {len(single_country)} single-country scraper(s) in parallel...")
        
        if sequential:
            # Debug mode: run everything sequentially
            for config in single_country:
                print(f"   Starting {config['country']}/{config['newspaper']}...")
                process = run_scraper_subprocess(config, log_dir, project_root, dry_run, urls_from_scratch)
                if process:
                    results = monitor_processes([process])
                    all_results.extend(results)
        else:
            # Parallel mode: start all at once
            for config in single_country:
                print(f"   Starting {config['country']}/{config['newspaper']}...")
                process = run_scraper_subprocess(config, log_dir, project_root, dry_run, urls_from_scratch)
                if process:
                    parallel_processes.append(process)
    
    # Run multi-country newspapers in separate sequential processes
    if multi_country and not sequential:
        print(f"\n🔗 Starting {len(multi_country)} multi-country newspaper group(s) in separate processes...")
        
        for group in multi_country:
            newspaper_name = group[0]["newspaper"]
            print(f"\n   Launching sequential process for: {newspaper_name} ({len(group)} countries)")
            
            # Create group config string for CLI argument
            group_config_str = ";".join([
                f"{cfg['country']},{cfg['newspaper']}"
                for cfg in group
            ])
            
            if not dry_run:
                # Launch a subprocess using the run_scraper module
                # This process runs independently and doesn't block parallel execution
                run_scraper_path = project_root / "src" / "text" / "scrapers" / "orchestration" / "run_scraper.py"
                cmd = [
                    "poetry", "run", "python",
                    str(run_scraper_path),
                    "--group", group_config_str,
                    "--project-root", str(project_root),
                    "--log-dir", str(log_dir),
                ]
                
                try:
                    # Start the sequential group process in the background
                    # Suppress stdout/stderr - all output goes to log files
                    process = subprocess.Popen(
                        cmd,
                        cwd=str(project_root),
                        start_new_session=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    process.newspaper_group = newspaper_name
                    sequential_processes.append(process)
                    print(f"      ✓ Sequential process started (PID: {process.pid})")
                except Exception as e:
                    print(f"      ❌ Failed to start sequential process: {e}")
            else:
                # Dry run: just show what would happen
                for config in group:
                    print(f"      [Sequential] Would run: {config['country']}/{config['newspaper']}")
    
    elif multi_country and sequential:
        # Debug mode: run multi-country groups sequentially in main process
        print(f"\n🔗 Processing {len(multi_country)} multi-country newspaper group(s) sequentially...")
        for group in multi_country:
            group_results = run_multi_country_group_sequential(group, log_dir, project_root, dry_run, urls_from_scratch)
            all_results.extend(group_results)
    
    # Monitor all processes (parallel + sequential) in unified display
    if (parallel_processes or sequential_processes) and not dry_run:
        total_count = len(parallel_processes) + len(sequential_processes)
        print(f"\n🔄 Monitoring {total_count} scraper(s)...")
        if sequential_processes:
            print("   (Multi-country newspapers run sequentially - output in logs)\n")
        else:
            print()
        
        # Create unified progress display
        progress, console = create_progress_display()
        
        # Track all processes and their tasks
        task_map = {}  # process -> task_id
        process_types = {}  # process -> 'parallel' or 'sequential'
        
        with progress:
            # Add parallel processes
            for process in parallel_processes:
                task_id = progress.add_task(
                    "[yellow]Running...",
                    country=process.country,
                    newspaper=process.newspaper,
                    total=100,
                    completed=0,
                )
                task_map[process] = task_id
                process_types[process] = 'parallel'
            
            # Add sequential group processes
            for process in sequential_processes:
                newspaper_group = getattr(process, 'newspaper_group', 'unknown')
                task_id = progress.add_task(
                    "[yellow]Running...",
                    country="multi-country",
                    newspaper=newspaper_group,
                    total=100,
                    completed=0,
                )
                task_map[process] = task_id
                process_types[process] = 'sequential'
            
            # Monitor all processes together
            all_processes = parallel_processes + sequential_processes
            remaining = list(all_processes)
            
            while remaining:
                for process in remaining[:]:
                    task_id = task_map[process]
                    process_type = process_types[process]
                    retcode = process.poll()
                    
                    if retcode is not None:
                        # Process finished
                        if process_type == 'parallel':
                            # Parallel process - parse log for detailed status
                            country = process.country
                            newspaper = process.newspaper
                            log_file = process.log_file
                            
                            if hasattr(process, 'log_handle'):
                                process.log_handle.close()
                            
                            status = parse_log_status(log_file, retcode)
                            
                            result = {
                                "country": country,
                                "newspaper": newspaper,
                                "log_file": log_file,
                                "exit_code": retcode,
                                "status": status,
                            }
                            all_results.append(result)
                            
                            # Update progress with detailed status
                            if status == "success":
                                progress.update(task_id, description="[green]✅ Completed", completed=100)
                            elif status == "warning":
                                progress.update(task_id, description="[yellow]⚠️  Completed (warnings)", completed=100)
                            else:
                                progress.update(task_id, description="[red]❌ Failed", completed=100)
                        else:
                            # Sequential process - simple exit code check
                            if retcode == 0:
                                progress.update(task_id, description="[green]✅ Completed", completed=100)
                            else:
                                progress.update(task_id, description="[red]❌ Failed", completed=100)
                        
                        remaining.remove(process)
                    else:
                        # Still running - update progress bar
                        current = progress.tasks[task_id].completed
                        if current < 90:
                            # Slower increment for sequential (they take longer)
                            increment = 1 if process_type == 'sequential' else 2
                            progress.update(task_id, completed=min(current + increment, 90))
                
                if remaining:
                    time.sleep(2.0)
    
    # Print summary
    if not dry_run and all_results:
        summarize_results(all_results)
    elif dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n⚠️  No results to summarize (sequential groups run independently)")
        print("   Check individual log files for multi-country newspaper results.")
    
    # Return success if no failures in monitored processes
    failed_count = sum(1 for r in all_results if r["status"] == "failed")
    return failed_count == 0
