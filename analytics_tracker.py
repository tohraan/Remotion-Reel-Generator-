"""
analytics_tracker.py - Track performance metrics and usage statistics

Features:
- Track rendering times and success rates
- Monitor resource usage (CPU, memory, disk)
- Generate performance reports
- Identify bottlenecks
- Export analytics data

Usage:
    python analytics_tracker.py --report
    python analytics_tracker.py --stats
    python analytics_tracker.py --export analytics.json
"""

import json
import sys
import time
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


class AnalyticsTracker:
    """Track and analyze reel generation performance"""
    
    def __init__(self, log_file: str = "analytics.jsonl"):
        self.log_file = Path(log_file)
        self.current_session = None
        
    def start_session(self, prompt: str) -> Dict:
        """Start tracking a new reel generation session"""
        
        self.current_session = {
            "session_id": f"{int(time.time())}_{hash(prompt) % 10000}",
            "prompt": prompt,
            "start_time": datetime.now().isoformat(),
            "start_timestamp": time.time(),
            
            # System stats at start
            "start_cpu_percent": psutil.cpu_percent(interval=1),
            "start_memory_mb": psutil.virtual_memory().used / (1024 * 1024),
            "start_disk_usage_mb": self._get_temp_disk_usage(),
            
            # Timing breakdowns
            "timings": {},
            
            # Metadata
            "status": "in_progress"
        }
        
        return self.current_session
    
    def log_phase(self, phase_name: str, duration: float):
        """Log timing for a specific phase"""
        if self.current_session:
            self.current_session["timings"][phase_name] = round(duration, 2)
    
    def end_session(self, status: str = "success", output_path: str = None, error: str = None):
        """End current session and save analytics"""
        
        if not self.current_session:
            return
        
        end_time = time.time()
        
        self.current_session.update({
            "end_time": datetime.now().isoformat(),
            "total_duration": round(end_time - self.current_session["start_timestamp"], 2),
            "status": status,
            
            # System stats at end
            "end_cpu_percent": psutil.cpu_percent(interval=1),
            "end_memory_mb": psutil.virtual_memory().used / (1024 * 1024),
            "end_disk_usage_mb": self._get_temp_disk_usage(),
            
            # Memory delta
            "memory_delta_mb": round(
                (psutil.virtual_memory().used / (1024 * 1024)) - 
                self.current_session["start_memory_mb"], 
                2
            )
        })
        
        if output_path:
            self.current_session["output_path"] = output_path
            self.current_session["output_size_mb"] = round(
                Path(output_path).stat().st_size / (1024 * 1024), 2
            ) if Path(output_path).exists() else 0
        
        if error:
            self.current_session["error"] = error
        
        # Save to log file (JSONL format - one JSON per line)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(self.current_session) + '\n')
        
        session_copy = self.current_session.copy()
        self.current_session = None
        
        return session_copy
    
    def _get_temp_disk_usage(self) -> float:
        """Get disk usage of temp directory in MB"""
        temp_path = Path("assets/temp")
        if not temp_path.exists():
            return 0
        
        total_size = sum(
            f.stat().st_size for f in temp_path.rglob('*') if f.is_file()
        )
        return round(total_size / (1024 * 1024), 2)
    
    def load_sessions(self, days: Optional[int] = None) -> List[Dict]:
        """Load session history from log file"""
        
        if not self.log_file.exists():
            return []
        
        sessions = []
        cutoff_date = None
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    session = json.loads(line.strip())
                    
                    # Filter by date if specified
                    if cutoff_date:
                        session_date = datetime.fromisoformat(session["start_time"])
                        if session_date < cutoff_date:
                            continue
                    
                    sessions.append(session)
                except json.JSONDecodeError:
                    continue
        
        return sessions
    
    def generate_report(self, days: int = 7):
        """Generate comprehensive analytics report"""
        
        sessions = self.load_sessions(days=days)
        
        if not sessions:
            print(f"❌ No sessions found in the last {days} days")
            return
        
        # Calculate statistics
        successful = [s for s in sessions if s["status"] == "success"]
        failed = [s for s in sessions if s["status"] == "failed"]
        
        total_count = len(sessions)
        success_count = len(successful)
        fail_count = len(failed)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        # Timing statistics
        if successful:
            durations = [s["total_duration"] for s in successful]
            avg_duration = statistics.mean(durations)
            median_duration = statistics.median(durations)
            min_duration = min(durations)
            max_duration = max(durations)
        else:
            avg_duration = median_duration = min_duration = max_duration = 0
        
        # Phase breakdown
        phase_times = defaultdict(list)
        for session in successful:
            for phase, duration in session.get("timings", {}).items():
                phase_times[phase].append(duration)
        
        # Resource usage
        if successful:
            avg_memory = statistics.mean([s.get("memory_delta_mb", 0) for s in successful])
            avg_output_size = statistics.mean([s.get("output_size_mb", 0) for s in successful if s.get("output_size_mb")])
        else:
            avg_memory = avg_output_size = 0
        
        # Print report
        print(f"\n{'='*70}")
        print(f"📊 ANALYTICS REPORT - Last {days} Days")
        print(f"{'='*70}\n")
        
        print(f"📈 Overview:")
        print(f"  • Total Reels Generated:  {total_count}")
        print(f"  • Successful:             {success_count} ({success_rate:.1f}%)")
        print(f"  • Failed:                 {fail_count}")
        print(f"  • Date Range:             {sessions[-1]['start_time'][:10]} to {sessions[0]['start_time'][:10]}")
        
        print(f"\n⏱️  Performance:")
        print(f"  • Average Duration:       {avg_duration:.2f}s")
        print(f"  • Median Duration:        {median_duration:.2f}s")
        print(f"  • Fastest:                {min_duration:.2f}s")
        print(f"  • Slowest:                {max_duration:.2f}s")
        
        if phase_times:
            print(f"\n🔧 Phase Breakdown (Average):")
            for phase, times in sorted(phase_times.items(), key=lambda x: -statistics.mean(x[1])):
                avg_time = statistics.mean(times)
                percentage = (avg_time / avg_duration * 100) if avg_duration > 0 else 0
                print(f"  • {phase:20s} {avg_time:6.2f}s ({percentage:5.1f}%)")
        
        print(f"\n💾 Resource Usage:")
        print(f"  • Avg Memory Delta:       {avg_memory:.2f} MB")
        print(f"  • Avg Output File Size:   {avg_output_size:.2f} MB")
        
        # Error analysis
        if failed:
            print(f"\n❌ Failure Analysis ({fail_count} failures):")
            error_counts = defaultdict(int)
            for session in failed:
                error = session.get("error", "Unknown error")
                # Truncate error to first line
                error_short = error.split('\n')[0][:50]
                error_counts[error_short] += 1
            
            for error, count in sorted(error_counts.items(), key=lambda x: -x[1])[:5]:
                print(f"  • {error}: {count} occurrences")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if avg_duration > 60:
            print(f"  ⚠️  Average duration exceeds 60s target")
            # Find slowest phase
            if phase_times:
                slowest_phase = max(phase_times.items(), key=lambda x: statistics.mean(x[1]))
                print(f"     Bottleneck: {slowest_phase[0]} ({statistics.mean(slowest_phase[1]):.2f}s avg)")
        
        if success_rate < 90:
            print(f"  ⚠️  Success rate below 90%")
            print(f"     Review error logs for common issues")
        
        if avg_memory > 500:
            print(f"  ⚠️  High memory usage detected")
            print(f"     Consider optimizing image/video processing")
        
        if not phase_times:
            print(f"  ℹ️  No phase timing data - update main.py to log phases")
        
        print(f"\n{'='*70}\n")
    
    def export_data(self, output_file: str, days: Optional[int] = None):
        """Export analytics data to JSON"""
        
        sessions = self.load_sessions(days=days)
        
        if not sessions:
            print("❌ No sessions to export")
            return
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_sessions": len(sessions),
            "date_range_days": days,
            "sessions": sessions
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Exported {len(sessions)} sessions to {output_file}")
    
    def get_stats(self):
        """Get quick statistics"""
        
        sessions = self.load_sessions(days=30)  # Last 30 days
        
        if not sessions:
            print("❌ No sessions found")
            return
        
        successful = [s for s in sessions if s["status"] == "success"]
        
        print(f"\n📊 Quick Stats (Last 30 Days):")
        print(f"  • Total:      {len(sessions)}")
        print(f"  • Successful: {len(successful)}")
        print(f"  • Failed:     {len(sessions) - len(successful)}")
        
        if successful:
            avg_time = statistics.mean([s["total_duration"] for s in successful])
            print(f"  • Avg Time:   {avg_time:.2f}s")
        
        print()


def main():
    """Main entry point"""
    
    tracker = AnalyticsTracker()
    
    if len(sys.argv) < 2:
        print("""
Usage:
    python analytics_tracker.py --report [days]     # Generate report (default: 7 days)
    python analytics_tracker.py --stats              # Quick stats
    python analytics_tracker.py --export <file>      # Export data to JSON
    python analytics_tracker.py --clear              # Clear all analytics data
    
Examples:
    python analytics_tracker.py --report             # Last 7 days
    python analytics_tracker.py --report 30          # Last 30 days
    python analytics_tracker.py --export data.json
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "--report" or command == "-r":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        tracker.generate_report(days=days)
    
    elif command == "--stats" or command == "-s":
        tracker.get_stats()
    
    elif command == "--export" or command == "-e":
        if len(sys.argv) < 3:
            print("❌ Usage: --export <output_file.json>")
            sys.exit(1)
        
        output_file = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else None
        tracker.export_data(output_file, days=days)
    
    elif command == "--clear":
        response = input("⚠️  This will delete all analytics data. Continue? (y/n): ")
        if response.lower() == 'y':
            if tracker.log_file.exists():
                tracker.log_file.unlink()
                print("✅ Analytics data cleared")
            else:
                print("ℹ️  No analytics data to clear")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()