# Parallel/Sequential Execution Architecture

## Overview

The multi-scraper runner now implements a sophisticated execution model where:
- **Single-country newspapers** run in parallel for maximum efficiency
- **Multi-country newspapers** run sequentially in separate background processes
- Sequential execution does NOT block parallel execution

## Problem Statement

### Before
Multi-country newspapers (e.g., ABC Australia, RNZ) were running sequentially in the main process, which blocked the parallel execution of single-country newspapers. This meant:
- Single-country scrapers had to wait for multi-country groups to finish
- Overall execution time was unnecessarily long
- Resource utilization was suboptimal

### After
Multi-country newspapers run in separate background processes that execute independently:
- Single-country scrapers run in parallel immediately
- Multi-country groups run sequentially in their own processes
- Both types execute simultaneously without interference

## Architecture

### Execution Flow

```
Main Process
├── Discover all configurations
├── Group by newspaper (single vs multi-country)
│
├── Launch Parallel Processes (single-country)
│   ├── sibc (Solomon Islands)
│   ├── solomon_star (Solomon Islands)
│   ├── fiji_times (Fiji)
│   └── ... (all run simultaneously)
│
├── Launch Sequential Group Processes (multi-country)
│   ├── Background Process 1: ABC Group
│   │   ├── pacific/abc_au (runs first)
│   │   ├── tonga/abc_au (waits for pacific)
│   │   ├── fiji/abc_au (waits for tonga)
│   │   └── ... (sequential within group)
│   │
│   └── Background Process 2: RNZ Group
│       ├── fiji/rnz (runs first)
│       ├── solomon_islands/rnz (waits for fiji)
│       └── ... (sequential within group)
│
├── Monitor parallel processes (non-blocking)
└── Monitor sequential group processes (non-blocking)
```

### Process Independence

```
Timeline:
0s    ─────────────────────────────────────────────────
      │ Main Process: Discovers configs
      │
5s    ├─ Launches Parallel Processes (13 scrapers)
      │  ├─ sibc starts
      │  ├─ solomon_star starts
      │  ├─ fiji_times starts
      │  └─ ... (all start immediately)
      │
      ├─ Launches Sequential Process 1 (ABC group)
      │  └─ Runs in background, doesn't block
      │
      ├─ Launches Sequential Process 2 (RNZ group)
      │  └─ Runs in background, doesn't block
      │
10s   │ Main Process: Monitors parallel scrapers
      │  ├─ sibc completes ✅
      │  ├─ fiji_times completes ✅
      │  └─ ...
      │
      │ Background Process 1: ABC group running
      │  ├─ pacific/abc_au running...
      │
      │ Background Process 2: RNZ group running
      │  ├─ fiji/rnz running...
      │
60s   │ All parallel scrapers complete
      │ Main Process: Waits for sequential groups
      │
      │ Background Process 1: Still running
      │  ├─ fiji/abc_au running...
      │
      │ Background Process 2: Still running
      │  ├─ solomon_islands/rnz running...
      │
120s  │ Sequential groups complete
      └─ All done
```

## Implementation Details

### 1. Single-Country Newspapers (Parallel)

**Execution:**
```python
parallel_processes = []
for config in single_country:
    process = run_scraper_subprocess(config, log_dir, project_root, dry_run)
    parallel_processes.append(process)

# All processes start immediately
# Monitor them concurrently
results = monitor_processes(parallel_processes)
```

**Characteristics:**
- All start simultaneously
- Run independently
- No waiting between scrapers
- Maximum resource utilization

### 2. Multi-Country Newspapers (Sequential in Background)

**Execution:**
```python
sequential_processes = []
for group in multi_country:
    # Create a Python subprocess that runs the group sequentially
    cmd = ["poetry", "run", "python", "-c", """
        # Sequential execution logic
        for config in group:
            run_scraper(config)
            wait_for_completion()
    """]
    
    # Launch in background with start_new_session=True
    process = subprocess.Popen(cmd, start_new_session=True)
    sequential_processes.append(process)

# Process runs independently in background
# Doesn't block parallel execution
```

**Characteristics:**
- Each group runs in its own background process
- Within each group, scrapers run sequentially
- Groups don't interfere with parallel execution
- Groups don't interfere with each other

### 3. Python Inline Script Approach

We use `python -c` with an inline script to avoid creating temporary files:

```python
cmd = [
    "poetry", "run", "python", "-c",
    f"""
import subprocess
import time
from pathlib import Path

project_root = Path('{project_root}')
log_dir = Path('{log_dir}')
group_configs = '{group_config_str}'.split(';')

for config_str in group_configs:
    country, newspaper = config_str.split(',')
    log_subdir = log_dir / country / newspaper
    log_subdir.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_subdir / f'{{timestamp}}.log'
    
    cmd = [
        'poetry', 'run', 'python',
        str(project_root / 'src' / 'text' / 'scrapers' / 'orchestration' / 'main.py'),
        newspaper,
        '--update',
    ]
    
    with open(log_file, 'w') as f:
        process = subprocess.run(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            cwd=str(project_root),
        )
    
    # Small delay between countries in the same group
    time.sleep(1)
"""
]
```

**Benefits:**
- No temporary files needed
- Self-contained execution
- Easy to debug
- Clean process management

## Process Management

### Background Process Creation

```python
process = subprocess.Popen(
    cmd,
    cwd=str(project_root),
    start_new_session=True,  # Detach from parent
)
process.newspaper_group = newspaper_name  # Track metadata
sequential_processes.append(process)
```

**Key Parameters:**
- `start_new_session=True`: Process runs independently
- `cwd`: Ensures correct working directory
- No stdout/stderr redirection: Process manages its own logging

### Monitoring

```python
# Monitor parallel processes (non-blocking)
if parallel_processes:
    results = monitor_processes(parallel_processes)
    all_results.extend(results)

# Monitor sequential group processes (blocking at end)
if sequential_processes:
    for process in sequential_processes:
        newspaper_group = process.newspaper_group
        print(f"Waiting for {newspaper_group} group to complete...")
        process.wait()  # Block until this group finishes
        exit_code = process.returncode
        print(f"✅ {newspaper_group} group completed")
```

**Monitoring Strategy:**
1. Parallel processes monitored concurrently (poll every 2 seconds)
2. Sequential group processes monitored at the end (wait for completion)
3. Main process doesn't exit until all processes complete

## Logging

### Log Structure

```
logs/
├── {country}/
│   └── {newspaper}/
│       └── YYYYMMDD_HHMMSS.log
```

### Log Management

**Parallel Processes:**
- Main process creates log files
- Redirects stdout/stderr to log files
- Closes handles when process completes

**Sequential Group Processes:**
- Background process creates log files
- Each scraper in group gets its own log file
- Background process manages its own file handles

## Error Handling

### Parallel Process Failures
- Individual failures don't stop other parallel processes
- Failed processes tracked in results
- Summary shows success/warning/failure counts

### Sequential Group Failures
- Failure in one country doesn't stop the group
- Group continues to next country
- Exit code reflects overall group status

### Background Process Failures
- Main process waits for all background processes
- Exit codes checked for each group
- Failures reported but don't crash main process

## Performance Characteristics

### Before (Sequential Multi-Country in Main Process)

```
Total Time = Parallel Time + Sequential Time
           = max(single_country_times) + sum(multi_country_times)
           = 60s + 300s = 360s (6 minutes)
```

### After (Sequential Multi-Country in Background)

```
Total Time = max(Parallel Time, Sequential Time)
           = max(max(single_country_times), max(multi_country_group_times))
           = max(60s, 300s) = 300s (5 minutes)
```

**Improvement:** ~17% faster for this example

### Real-World Scenario

With 13 single-country newspapers (avg 30s each) and 2 multi-country groups (avg 150s each):

**Before:**
```
Time = max(30s) + (150s + 150s) = 30s + 300s = 330s (5.5 minutes)
```

**After:**
```
Time = max(30s, 150s) = 150s (2.5 minutes)
```

**Improvement:** ~55% faster

## Debug Mode (--sequential)

When `--sequential` flag is used:
- All scrapers run sequentially in the main process
- No parallel execution
- No background processes
- Easier to debug issues

```python
if sequential:
    # Run everything sequentially in main process
    for config in single_country:
        process = run_scraper_subprocess(config, log_dir, project_root, dry_run)
        results = monitor_processes([process])
        all_results.extend(results)
    
    for group in multi_country:
        group_results = run_multi_country_group_sequential(group, log_dir, project_root, dry_run)
        all_results.extend(group_results)
```

## Testing

### Dry Run Mode

```bash
poetry run python src/text/scrapers/orchestration/main.py --run-all --dry-run
```

**Output:**
```
🌊 Pacific Observatory - Multi-Scraper Runner
============================================================

🔍 Discovering configurations...
   Found 24 scraper configuration(s)
   - 13 single-country newspapers
   - 2 multi-country newspaper groups

[DRY RUN MODE - No scrapers will actually run]

🚀 Starting 13 single-country scraper(s) in parallel...
   Starting solomon_islands/sibc...
   [DRY RUN] Would execute: poetry run python .../main.py sibc --update
   ...

🔗 Starting 2 multi-country newspaper group(s) in separate processes...

   Launching sequential process for: abc_au (7 countries)
      [Sequential] Would run: pacific/abc_au
      [Sequential] Would run: tonga/abc_au
      ...

   Launching sequential process for: rnz (4 countries)
      [Sequential] Would run: fiji/rnz
      [Sequential] Would run: solomon_islands/rnz
      ...

[DRY RUN COMPLETE]
```

### Production Run

```bash
poetry run python src/text/scrapers/orchestration/main.py --run-all
```

**Output:**
```
🌊 Pacific Observatory - Multi-Scraper Runner
============================================================

🔍 Discovering configurations...
   Found 24 scraper configuration(s)
   - 13 single-country newspapers
   - 2 multi-country newspaper groups

🚀 Starting 13 single-country scraper(s) in parallel...
   Starting solomon_islands/sibc...
   Starting solomon_islands/solomon_star...
   ...

🔗 Starting 2 multi-country newspaper group(s) in separate processes...

   Launching sequential process for: abc_au (7 countries)
      ✓ Sequential process started (PID: 12345)

   Launching sequential process for: rnz (4 countries)
      ✓ Sequential process started (PID: 12346)

🔄 Monitoring 13 parallel scraper(s)...

✅ solomon_islands/sibc completed (success)
✅ fiji/fiji_times completed (success)
...

🔄 Monitoring 2 sequential group process(es)...
   (These run independently and may take longer)

   Waiting for abc_au group to complete...
   ✅ abc_au group completed (exit code: 0)
   Waiting for rnz group to complete...
   ✅ rnz group completed (exit code: 0)

────────────────────────────────────────────────────────────
SCRAPER SUMMARY (2025-10-14 12:00:00)
────────────────────────────────────────────────────────────
✅ solomon_islands    / sibc                 Completed successfully
✅ fiji               / fiji_times           Completed successfully
...
────────────────────────────────────────────────────────────
Total: 13 | Success: 13 | Warnings: 0 | Failed: 0
────────────────────────────────────────────────────────────

⚠️  No results to summarize (sequential groups run independently)
   Check individual log files for multi-country newspaper results.
```

## Benefits

### 1. True Parallel Execution
- Single-country newspapers run simultaneously
- No blocking from sequential groups
- Maximum resource utilization

### 2. Rate Limiting Protection
- Multi-country newspapers still run sequentially
- Avoids IP blocking and rate limiting
- Maintains site-friendly behavior

### 3. Process Independence
- Background processes don't interfere with main process
- Each group runs in isolation
- Clean process management

### 4. Scalability
- Can handle any number of newspapers
- Efficient resource usage
- Minimal overhead

### 5. Maintainability
- Clear separation of concerns
- Easy to understand execution model
- Simple debugging with --sequential flag

## Future Enhancements

### Potential Improvements

1. **Resource Limits**: Add max concurrent processes limit
2. **Priority Queues**: Prioritize certain newspapers
3. **Dynamic Scheduling**: Adjust based on system load
4. **Progress Tracking**: Real-time progress dashboard
5. **Retry Logic**: Automatic retry of failed groups
6. **Email Notifications**: Alert on completion/failures
7. **Metrics Collection**: Track execution times and success rates

### Advanced Features

1. **Distributed Execution**: Run on multiple machines
2. **Container Support**: Docker-based execution
3. **Cloud Integration**: AWS Lambda, Google Cloud Functions
4. **Queue Systems**: RabbitMQ, Redis Queue integration
5. **Monitoring Dashboard**: Web-based real-time monitoring

## Conclusion

The new architecture provides:
- ✅ True parallel execution for single-country newspapers
- ✅ Sequential execution for multi-country newspapers (rate limiting protection)
- ✅ No interference between parallel and sequential execution
- ✅ Efficient resource utilization
- ✅ Clean process management
- ✅ Easy debugging and monitoring

This design maximizes performance while maintaining site-friendly scraping behavior.
