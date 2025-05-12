#!/usr/bin/env python3
"""
Ali Memory Visualizer

This tool visualizes Ali's emotional memory data, showing patterns, 
emotional states, and interaction history in a human-readable format.
"""

import os
import sys
import json
import argparse
import logging
import datetime
from pathlib import Path
from collections import Counter, defaultdict

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Ali.MemoryVisualizer")

class AliMemoryVisualizer:
    """Tool for visualizing and analyzing Ali's emotional memory."""
    
    def __init__(self, data_dir=None):
        """Initialize the memory visualizer."""
        self.data_dir = Path(data_dir) if data_dir else Path("data")
        self.memory_dir = self.data_dir / "memory"
        self.output_dir = Path("memory_analysis")
        self.output_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_memories": 0,
            "emotional_states": Counter(),
            "interaction_types": Counter(),
            "time_of_day": Counter(),
            "bond_progression": [],
            "sentiment_values": []
        }
    
    def load_memory_files(self):
        """Load all memory files."""
        if not self.memory_dir.exists():
            logger.error(f"Memory directory not found: {self.memory_dir}")
            return False
        
        memory_files = list(self.memory_dir.glob("*.json"))
        if not memory_files:
            logger.error("No memory files found")
            return False
        
        logger.info(f"Found {len(memory_files)} memory files")
        
        # Load and process all memory files
        all_memories = []
        for file_path in sorted(memory_files):
            try:
                with open(file_path, 'r') as f:
                    memories = json.load(f)
                    all_memories.extend(memories)
                    logger.debug(f"Loaded {len(memories)} memories from {file_path.name}")
            except Exception as e:
                logger.error(f"Error loading memory file {file_path.name}: {e}")
        
        self.stats["total_memories"] = len(all_memories)
        logger.info(f"Loaded {len(all_memories)} total memories")
        
        # Process memories for analysis
        self._analyze_memories(all_memories)
        
        return all_memories
    
    def _analyze_memories(self, memories):
        """Analyze memory entries to collect statistics."""
        bond_values = []
        timestamps = []
        
        for memory in memories:
            # Extract emotional state
            if "emotional_state" in memory:
                emotional_state = memory["emotional_state"].get("current", "neutral")
                self.stats["emotional_states"][emotional_state] += 1
            
            # Extract interaction type
            if "event" in memory:
                self.stats["interaction_types"][memory["event"]] += 1
            
            # Extract time of day
            if "timestamp" in memory:
                try:
                    timestamp = datetime.datetime.fromisoformat(memory["timestamp"])
                    hour = timestamp.hour
                    
                    # Categorize by time of day
                    if 5 <= hour < 12:
                        time_category = "morning"
                    elif 12 <= hour < 17:
                        time_category = "afternoon"
                    elif 17 <= hour < 22:
                        time_category = "evening"
                    else:
                        time_category = "night"
                    
                    self.stats["time_of_day"][time_category] += 1
                    
                    # Store timestamp for time-based analysis
                    timestamps.append(timestamp)
                except (ValueError, TypeError):
                    pass
            
            # Extract bond progression if available
            if "bond_level" in memory:
                try:
                    bond_value = float(memory["bond_level"])
                    if 0 <= bond_value <= 1:
                        if "timestamp" in memory:
                            try:
                                timestamp = datetime.datetime.fromisoformat(memory["timestamp"])
                                bond_values.append((timestamp, bond_value))
                            except (ValueError, TypeError):
                                pass
                except (ValueError, TypeError):
                    pass
            
            # Extract sentiment values
            if "sentiment" in memory:
                try:
                    sentiment = float(memory["sentiment"])
                    if -1 <= sentiment <= 1:
                        self.stats["sentiment_values"].append(sentiment)
                except (ValueError, TypeError):
                    pass
        
        # Sort bond values by timestamp
        bond_values.sort(key=lambda x: x[0])
        self.stats["bond_progression"] = bond_values
    
    def generate_text_report(self):
        """Generate a text-based report of memory statistics."""
        report_path = self.output_dir / "memory_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Ali Memory Analysis Report\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total Memories: {self.stats['total_memories']}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("Emotional States:\n")
            f.write("-" * 80 + "\n")
            for state, count in self.stats["emotional_states"].most_common():
                percentage = (count / self.stats["total_memories"]) * 100
                f.write(f"{state}: {count} ({percentage:.1f}%)\n")
            
            f.write("\n" + "-" * 80 + "\n")
            f.write("Interaction Types:\n")
            f.write("-" * 80 + "\n")
            for event_type, count in self.stats["interaction_types"].most_common():
                percentage = (count / self.stats["total_memories"]) * 100
                f.write(f"{event_type}: {count} ({percentage:.1f}%)\n")
            
            f.write("\n" + "-" * 80 + "\n")
            f.write("Time of Day Distribution:\n")
            f.write("-" * 80 + "\n")
            for time_period, count in self.stats["time_of_day"].most_common():
                percentage = (count / sum(self.stats["time_of_day"].values())) * 100
                f.write(f"{time_period}: {count} ({percentage:.1f}%)\n")
            
            # Sentiment analysis
            if self.stats["sentiment_values"]:
                f.write("\n" + "-" * 80 + "\n")
                f.write("Sentiment Analysis:\n")
                f.write("-" * 80 + "\n")
                sentiment_values = self.stats["sentiment_values"]
                avg_sentiment = sum(sentiment_values) / len(sentiment_values)
                positive = sum(1 for s in sentiment_values if s > 0.3)
                neutral = sum(1 for s in sentiment_values if -0.3 <= s <= 0.3)
                negative = sum(1 for s in sentiment_values if s < -0.3)
                
                f.write(f"Average Sentiment: {avg_sentiment:.2f}\n")
                f.write(f"Positive Interactions: {positive} ({positive/len(sentiment_values)*100:.1f}%)\n")
                f.write(f"Neutral Interactions: {neutral} ({neutral/len(sentiment_values)*100:.1f}%)\n")
                f.write(f"Negative Interactions: {negative} ({negative/len(sentiment_values)*100:.1f}%)\n")
            
            # Bond progression
            if self.stats["bond_progression"]:
                f.write("\n" + "-" * 80 + "\n")
                f.write("Bond Progression:\n")
                f.write("-" * 80 + "\n")
                bond_values = [b[1] for b in self.stats["bond_progression"]]
                initial_bond = bond_values[0]
                current_bond = bond_values[-1]
                
                f.write(f"Initial Bond Level: {initial_bond:.2f}\n")
                f.write(f"Current Bond Level: {current_bond:.2f}\n")
                f.write(f"Bond Change: {current_bond - initial_bond:+.2f}\n")
        
        logger.info(f"Text report generated at {report_path}")
        return report_path
    
    def generate_visualizations(self):
        """Generate visual representations of memory data."""
        if not MATPLOTLIB_AVAILABLE:
            logger.error("Matplotlib is required for visualizations but is not installed.")
            return False
        
        try:
            self._create_emotional_pie_chart()
            self._create_time_distribution_chart()
            self._create_bond_progression_chart()
            self._create_sentiment_analysis_chart()
            self._create_interaction_timeline()
            
            logger.info(f"Visualizations generated in {self.output_dir}")
            return True
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return False
    
    def _create_emotional_pie_chart(self):
        """Create a pie chart of emotional states."""
        if not self.stats["emotional_states"]:
            return
        
        plt.figure(figsize=(10, 7))
        
        # Get the top 8 emotions, group the rest as "Other"
        top_emotions = self.stats["emotional_states"].most_common(8)
        other_count = sum(count for emotion, count in self.stats["emotional_states"].items() 
                         if emotion not in [e[0] for e in top_emotions])
        
        # Prepare data for the pie chart
        labels = [emotion for emotion, _ in top_emotions]
        if other_count > 0:
            labels.append("Other")
        
        sizes = [count for _, count in top_emotions]
        if other_count > 0:
            sizes.append(other_count)
        
        # Custom colors for emotions
        colors = plt.cm.tab10(np.linspace(0, 1, len(labels)))
        
        # Create the pie chart
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, shadow=True)
        plt.axis('equal')
        plt.title('Distribution of Emotional States', size=16)
        
        # Save the chart
        plt.savefig(self.output_dir / "emotional_states.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_time_distribution_chart(self):
        """Create a bar chart of time of day distribution."""
        if not self.stats["time_of_day"]:
            return
        
        plt.figure(figsize=(10, 6))
        
        # Prepare data
        time_periods = ["morning", "afternoon", "evening", "night"]
        counts = [self.stats["time_of_day"].get(period, 0) for period in time_periods]
        
        # Create the bar chart
        bars = plt.bar(time_periods, counts, color=plt.cm.viridis(np.linspace(0.1, 0.9, len(time_periods))))
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height}',
                   ha='center', va='bottom')
        
        plt.title('Interaction Distribution by Time of Day', size=16)
        plt.ylabel('Number of Interactions')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Save the chart
        plt.savefig(self.output_dir / "time_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_bond_progression_chart(self):
        """Create a line chart showing bond level progression over time."""
        if not self.stats["bond_progression"]:
            return
        
        plt.figure(figsize=(12, 6))
        
        # Extract data
        dates = [bp[0] for bp in self.stats["bond_progression"]]
        bond_values = [bp[1] for bp in self.stats["bond_progression"]]
        
        # Create the line chart
        plt.plot(dates, bond_values, '-o', markersize=4, linewidth=2)
        
        # Format the x-axis to show dates nicely
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        
        plt.title('Bond Level Progression Over Time', size=16)
        plt.ylabel('Bond Level')
        plt.ylim(0, 1.05)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save the chart
        plt.savefig(self.output_dir / "bond_progression.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_sentiment_analysis_chart(self):
        """Create a histogram of sentiment values."""
        if not self.stats["sentiment_values"]:
            return
        
        plt.figure(figsize=(10, 6))
        
        # Create custom colormap: red for negative, yellow for neutral, green for positive
        colors = [(0.8, 0.2, 0.2), (0.9, 0.9, 0.2), (0.2, 0.8, 0.2)]
        cmap = LinearSegmentedColormap.from_list("sentiment_cmap", colors, N=100)
        
        # Create the histogram
        n, bins, patches = plt.hist(self.stats["sentiment_values"], bins=15, edgecolor='black', alpha=0.7)
        
        # Color the bars based on sentiment value
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        norm = plt.Normalize(-1, 1)
        for c, p in zip(bin_centers, patches):
            plt.setp(p, 'facecolor', cmap(norm(c)))
        
        plt.title('Distribution of Sentiment Values', size=16)
        plt.xlabel('Sentiment (-1 = Negative, +1 = Positive)')
        plt.ylabel('Frequency')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add vertical lines for reference
        plt.axvline(x=0, color='k', linestyle='--')
        plt.text(0.02, plt.ylim()[1]*0.9, 'Neutral', rotation=90, verticalalignment='top')
        
        # Save the chart
        plt.savefig(self.output_dir / "sentiment_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_interaction_timeline(self):
        """Create a timeline visualization of interactions by type."""
        # Prepare data
        events_by_date = defaultdict(Counter)
        
        for memory in self.load_memory_files():
            if "timestamp" in memory and "event" in memory:
                try:
                    timestamp = datetime.datetime.fromisoformat(memory["timestamp"])
                    date = timestamp.date()
                    event = memory["event"]
                    events_by_date[date][event] += 1
                except (ValueError, TypeError):
                    continue
        
        if not events_by_date:
            return
        
        # Get the top 5 most common event types
        all_events = Counter()
        for date_counter in events_by_date.values():
            all_events.update(date_counter)
        
        top_events = [event for event, _ in all_events.most_common(5)]
        
        # Prepare data for plotting
        dates = sorted(events_by_date.keys())
        event_data = {event: [events_by_date[date][event] for date in dates] for event in top_events}
        
        # Create the stacked area chart
        plt.figure(figsize=(14, 7))
        
        # Convert dates to matplotlib format
        x = [mdates.date2num(datetime.datetime.combine(d, datetime.time())) for d in dates]
        
        # Prepare stacked data
        y_stack = np.zeros(len(dates))
        colors = plt.cm.tab10(np.linspace(0, 1, len(top_events)))
        
        for i, event in enumerate(top_events):
            y = np.array(event_data[event])
            plt.fill_between(x, y_stack, y_stack + y, color=colors[i], alpha=0.7, label=event)
            y_stack += y
        
        # Format the plot
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        
        plt.title('Interaction Timeline by Event Type', size=16)
        plt.ylabel('Number of Interactions')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper left')
        
        # Save the chart
        plt.savefig(self.output_dir / "interaction_timeline.png", dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """Main function for the memory visualizer."""
    parser = argparse.ArgumentParser(description="Ali Memory Visualizer")
    parser.add_argument("--data-dir", help="Ali data directory", default="data")
    parser.add_argument("--output-dir", help="Output directory for reports and visualizations", default="memory_analysis")
    parser.add_argument("--no-visuals", action="store_true", help="Generate text report only (no visualizations)")
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" Ali Memory Visualizer ".center(70, "="))
    print("="*70)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Create visualizer
    visualizer = AliMemoryVisualizer(args.data_dir)
    visualizer.output_dir = output_dir
    
    # Load memory data
    print("\nLoading memory data...")
    memories = visualizer.load_memory_files()
    
    if not memories:
        print("No memory data found or error loading data. Exiting.")
        return 1
    
    # Generate text report
    print("Generating text report...")
    report_path = visualizer.generate_text_report()
    print(f"Report saved to: {report_path}")
    
    # Generate visualizations
    if not args.no_visuals:
        if MATPLOTLIB_AVAILABLE:
            print("Generating visualizations...")
            visualizer.generate_visualizations()
            print(f"Visualizations saved to: {output_dir}")
        else:
            print("\nWarning: Matplotlib is required for visualizations but is not installed.")
            print("To install matplotlib, run: pip install matplotlib")
            print("Only text report was generated.")
    
    print("\nMemory analysis complete!")
    print(f"Total memories analyzed: {visualizer.stats['total_memories']}")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
