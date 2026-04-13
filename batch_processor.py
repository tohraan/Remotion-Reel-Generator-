"""
batch_processor.py - Bulk Instagram Reel Generation

Usage:
    python batch_processor.py prompts.txt
    python batch_processor.py --interactive
    python batch_processor.py --csv data.csv
"""

import asyncio
import csv
import sys
import time
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import json

# Import from main.py
from main import ReelOrchestrator
from config import Config


class BatchProcessor:
    """Process multiple reel prompts in sequence or parallel"""
    
    def __init__(self, output_manifest: bool = True):
        self.results = []
        self.output_manifest = output_manifest
        self.start_time = None
        
    async def process_single(self, prompt: str, index: int) -> Dict:
        """Process single prompt and return result"""
        print(f"\n{'='*60}")
        print(f"🎬 [{index}] Processing: {prompt[:50]}...")
        print(f"{'='*60}")
        
        try:
            start = time.time()
            output_path = await ReelOrchestrator.create_reel(prompt)
            elapsed = time.time() - start
            
            result = {
                "index": index,
                "prompt": prompt,
                "status": "success",
                "output_path": output_path,
                "duration_seconds": round(elapsed, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ [{index}] Success in {elapsed:.2f}s: {output_path}")
            
        except Exception as e:
            result = {
                "index": index,
                "prompt": prompt,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"❌ [{index}] Failed: {str(e)}")
        
        return result
    
    async def process_sequential(self, prompts: List[str]) -> List[Dict]:
        """Process prompts one by one"""
        print(f"\n🔄 Starting SEQUENTIAL batch processing: {len(prompts)} prompts")
        self.start_time = time.time()
        
        for i, prompt in enumerate(prompts, 1):
            result = await self.process_single(prompt, i)
            self.results.append(result)
        
        return self.results
    
    async def process_parallel(self, prompts: List[str], max_concurrent: int = 2) -> List[Dict]:
        """
        Process prompts in parallel (limited concurrency to avoid resource exhaustion)
        WARNING: Parallel rendering is resource-intensive!
        """
        print(f"\n⚡ Starting PARALLEL batch processing: {len(prompts)} prompts")
        print(f"   Max concurrent: {max_concurrent}")
        self.start_time = time.time()
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(prompt: str, index: int):
            async with semaphore:
                return await self.process_single(prompt, index)
        
        tasks = [
            process_with_semaphore(prompt, i+1) 
            for i, prompt in enumerate(prompts)
        ]
        
        self.results = await asyncio.gather(*tasks)
        return self.results
    
    def save_manifest(self, filename: str = None):
        """Save processing manifest as JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{Config.OUTPUT_DIR}/batch_manifest_{timestamp}.json"
        
        total_time = time.time() - self.start_time if self.start_time else 0
        
        manifest = {
            "batch_info": {
                "total_prompts": len(self.results),
                "successful": sum(1 for r in self.results if r["status"] == "success"),
                "failed": sum(1 for r in self.results if r["status"] == "failed"),
                "total_time_seconds": round(total_time, 2),
                "average_time_per_reel": round(total_time / len(self.results), 2) if self.results else 0,
                "timestamp": datetime.now().isoformat()
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n📋 Manifest saved: {filename}")
        return filename
    
    def print_summary(self):
        """Print batch processing summary"""
        total_time = time.time() - self.start_time if self.start_time else 0
        successful = sum(1 for r in self.results if r["status"] == "success")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        
        print(f"\n{'='*60}")
        print(f"📊 BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total Prompts:    {len(self.results)}")
        print(f"✅ Successful:    {successful}")
        print(f"❌ Failed:        {failed}")
        print(f"⏱️  Total Time:    {total_time:.2f}s")
        print(f"📈 Avg Per Reel:  {total_time/len(self.results):.2f}s" if self.results else "N/A")
        print(f"{'='*60}\n")
        
        if failed > 0:
            print("Failed prompts:")
            for r in self.results:
                if r["status"] == "failed":
                    print(f"  • [{r['index']}] {r['prompt'][:40]}... - {r['error']}")


def load_prompts_from_file(filepath: str) -> List[str]:
    """Load prompts from text file (one per line)"""
    with open(filepath, 'r') as f:
        prompts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return prompts


def load_prompts_from_csv(filepath: str, column: str = "prompt") -> List[str]:
    """Load prompts from CSV file"""
    prompts = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if column in row and row[column].strip():
                prompts.append(row[column].strip())
    return prompts


def interactive_mode() -> List[str]:
    """Interactive prompt entry mode"""
    print("\n🎨 Interactive Batch Mode")
    print("Enter prompts (one per line). Type 'done' when finished.\n")
    
    prompts = []
    index = 1
    
    while True:
        prompt = input(f"[{index}] Prompt: ").strip()
        
        if prompt.lower() == 'done':
            break
        
        if prompt:
            prompts.append(prompt)
            index += 1
    
    return prompts


async def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("""
Usage:
    python batch_processor.py prompts.txt              # Process from text file
    python batch_processor.py --csv data.csv           # Process from CSV
    python batch_processor.py --interactive            # Interactive mode
    python batch_processor.py --parallel prompts.txt   # Parallel processing (experimental)
    
Example prompts.txt:
    The science of dreams
    5 facts about ancient Egypt
    How chocolate is made
    # This is a comment (ignored)
    Future of space exploration
        """)
        sys.exit(1)
    
    # Parse arguments
    parallel_mode = False
    csv_mode = False
    interactive = False
    
    if "--parallel" in sys.argv:
        parallel_mode = True
        sys.argv.remove("--parallel")
    
    if "--csv" in sys.argv:
        csv_mode = True
        sys.argv.remove("--csv")
    
    if "--interactive" in sys.argv:
        interactive = True
    
    # Load prompts
    if interactive:
        prompts = interactive_mode()
    elif csv_mode:
        if len(sys.argv) < 2:
            print("❌ CSV file path required")
            sys.exit(1)
        prompts = load_prompts_from_csv(sys.argv[1])
    else:
        if len(sys.argv) < 2:
            print("❌ Prompts file path required")
            sys.exit(1)
        prompts = load_prompts_from_file(sys.argv[1])
    
    if not prompts:
        print("❌ No prompts found!")
        sys.exit(1)
    
    print(f"\n✅ Loaded {len(prompts)} prompts")
    
    # Confirm before processing
    response = input(f"\nProceed with {'PARALLEL' if parallel_mode else 'SEQUENTIAL'} processing? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Process batch
    processor = BatchProcessor()
    
    try:
        if parallel_mode:
            # Parallel processing (max 2 concurrent to avoid memory issues)
            await processor.process_parallel(prompts, max_concurrent=2)
        else:
            # Sequential processing (safer, recommended)
            await processor.process_sequential(prompts)
        
        # Print summary
        processor.print_summary()
        
        # Save manifest
        if processor.output_manifest:
            processor.save_manifest()
        
        print("\n🎉 Batch processing complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        processor.print_summary()
        if processor.results:
            processor.save_manifest()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())