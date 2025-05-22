import os
import sys
import logging
import time
import psutil
import subprocess
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('process_cleaner')

def kill_chrome_processes(kill_all_chrome=False, verbose=True):
    """
    Kill ChromeDriver processes and automation-related Chrome processes
    
    Args:
        kill_all_chrome (bool): If True, kill ALL Chrome processes (dangerous on workstations)
        verbose (bool): Whether to print detailed information about each process
        
    Returns:
        dict: Statistics about killed processes
    """
    killed_stats = {
        "chromedriver": 0,
        "chrome_automation": 0,
        "total": 0
    }
    
    # These are command line arguments that indicate a Chrome process is for automation
    automation_indicators = [
        "--test-type",
        "--disable-extensions",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--no-sandbox",
        "--headless",
        "webdriver",
        "chromedriver",
        "--remote-debugging-port"
    ]
    
    logger.info("Searching for Chrome automation processes")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ""
            proc_cmdline = ' '.join(proc.info['cmdline'] or []).lower()
            
            # 1. Definitely kill all ChromeDriver processes
            if "chromedriver" in proc_name:
                process_type = "chromedriver"
                kill_reason = "ChromeDriver process"
            
            # 2. For Chrome processes, check if it's automation-related
            elif "chrome" in proc_name and not kill_all_chrome:
                # Only kill Chrome instances that have automation-related command line args
                if any(indicator in proc_cmdline for indicator in automation_indicators):
                    process_type = "chrome_automation"
                    kill_reason = "Automation Chrome with flags: " + ", ".join(
                        [ind for ind in automation_indicators if ind in proc_cmdline][:2]  # Show first 2 matches
                    )
                else:
                    # Skip this Chrome process - likely a user browser
                    if verbose:
                        logger.debug(f"Skipping user Chrome process: PID={proc.pid}")
                    continue
            
            # 3. If kill_all_chrome is True, kill every Chrome process
            elif "chrome" in proc_name and kill_all_chrome:
                process_type = "chrome_automation"  # We categorize them with automation for stats
                kill_reason = "All Chrome processes (kill_all_chrome=True)"
            
            # Not a target process
            else:
                continue
                
            # Get process details for logging
            pid = proc.pid
            try:
                create_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                          time.localtime(proc.create_time()))
                memory_mb = proc.memory_info().rss / (1024 * 1024)
            except:
                create_time = "Unknown"
                memory_mb = 0
            
            if verbose:
                logger.info(f"Killing {process_type}: PID={pid}, "
                           f"Created={create_time}, Memory={memory_mb:.1f}MB, Reason: {kill_reason}")
            
            # Kill the process
            try:
                proc.kill()
                killed_stats[process_type] += 1
                killed_stats["total"] += 1
            except Exception as e:
                logger.warning(f"Failed to kill process {pid}: {str(e)}")
                
                # Try harder on Windows with taskkill
                if sys.platform == 'win32':
                    try:
                        subprocess.call(['taskkill', '/F', '/PID', str(pid)])
                        logger.info(f"Killed process {pid} using taskkill")
                        killed_stats[process_type] += 1
                        killed_stats["total"] += 1
                    except Exception as e2:
                        logger.error(f"Failed to use taskkill: {str(e2)}")
        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Log summary
    logger.info(f"Process cleanup complete. Killed {killed_stats['total']} processes "
               f"({killed_stats['chromedriver']} ChromeDriver, "
               f"{killed_stats['chrome_automation']} automation Chrome instances)")
    
    return killed_stats

def wait_and_verify(seconds=2):
    """Wait and verify automation processes are gone"""
    logger.info(f"Waiting {seconds} seconds to verify processes are terminated...")
    time.sleep(seconds)
    
    remaining = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ""
            proc_cmdline = ' '.join(proc.info['cmdline'] or []).lower()
            
            # Check for ChromeDriver
            if "chromedriver" in proc_name:
                remaining.append(f"{proc_name} (PID: {proc.pid})")
                continue
                
            # Check for automation Chrome
            automation_indicators = ["--test-type", "--headless", "webdriver", "--remote-debugging-port"]
            if "chrome" in proc_name and any(indicator in proc_cmdline for indicator in automation_indicators):
                remaining.append(f"{proc_name} - automation (PID: {proc.pid})")
        except:
            continue
    
    if remaining:
        logger.warning(f"Found {len(remaining)} remaining automation processes after cleanup")
        for proc in remaining[:5]:  # Show first 5 only
            logger.warning(f"  - {proc}")
        if len(remaining) > 5:
            logger.warning(f"  ... and {len(remaining) - 5} more")
    else:
        logger.info("No Chrome automation processes remaining - cleanup successful")
    
    return len(remaining) == 0

if __name__ == "__main__":
    # Directly specify parameters here
    stats = kill_chrome_processes(kill_all_chrome=False, verbose=True)
    
    # Verify
    wait_and_verify()
    
    # Exit with failure if nothing was killed and there are still processes
    if stats["total"] == 0 and not wait_and_verify():
        sys.exit(1)
