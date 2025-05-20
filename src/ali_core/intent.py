"""
Ali Intent Module
---------------
Implements the 'Intent Crawler' and 'Task Guardian' aspects from the Ali concept:
- Advanced intent recognition
- Proactive task completion
- Pattern recognition in user behavior
- Predictive assistance

This module handles understanding what the user wants or needs, even before they ask.
"""

import logging
import json
import re
import random
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

logger = logging.getLogger("Ali.Intent")

class AliIntent:
    """Intent recognition and proactive task management."""
    
    def __init__(self, user_id="MasterChief"):
        """Initialize the intent recognition system."""
        self.user_id = user_id
        self.intent_patterns = {}
        self.behavior_history = []
        self.task_queue = []
        self.recurring_tasks = []
        self.active = True
        self.background_thread = None
        
        # Intent confidence thresholds
        self.thresholds = {
            "auto_complete": 0.8,    # How sure we need to be to auto-complete a task
            "suggestion": 0.6,       # Threshold to suggest a task
            "prediction": 0.7,       # Threshold to predict user intent
            "routine": 0.75          # Threshold to establish routine
        }
        
        # Create data directories
        self.intent_data_path = Path("data/intent")
        self.intent_data_path.mkdir(parents=True, exist_ok=True)
        
        # Load intent data if available
        self._load_intent_data()
        
        logger.info(f"Ali Intent system initialized for user: {user_id}")
    
    def _load_intent_data(self):
        """Load saved intent patterns and behavior history."""
        intent_file = self.intent_data_path / f"{self.user_id.lower()}_intent.json"
        
        if intent_file.exists():
            try:
                with open(intent_file, 'r') as f:
                    data = json.load(f)
                
                # Update attributes
                self.intent_patterns = data.get("intent_patterns", {})
                self.behavior_history = data.get("behavior_history", [])
                self.task_queue = data.get("task_queue", [])
                self.recurring_tasks = data.get("recurring_tasks", [])
                self.thresholds = data.get("thresholds", self.thresholds)
                
                logger.info(f"Loaded intent data for {self.user_id}")
            except Exception as e:
                logger.error(f"Error loading intent data: {e}")
    
    def save_intent_data(self):
        """Save intent data to persistent storage."""
        intent_file = self.intent_data_path / f"{self.user_id.lower()}_intent.json"
        
        try:
            # Clean up old history entries before saving
            # Keep last 100 entries
            if len(self.behavior_history) > 100:
                self.behavior_history = self.behavior_history[-100:]
            
            intent_data = {
                "user_id": self.user_id,
                "intent_patterns": self.intent_patterns,
                "behavior_history": self.behavior_history,
                "task_queue": self.task_queue,
                "recurring_tasks": self.recurring_tasks,
                "thresholds": self.thresholds,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(intent_file, 'w') as f:
                json.dump(intent_data, f, indent=2)
                
            logger.info(f"Saved intent data for {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving intent data: {e}")
            return False
    
    def start_background_processing(self):
        """Start background thread for intent processing and task execution."""
        if self.background_thread and self.background_thread.is_alive():
            logger.warning("Background processing already running")
            return False
        
        try:
            self.active = True
            self.background_thread = threading.Thread(
                target=self._background_loop,
                daemon=True
            )
            self.background_thread.start()
            logger.info("Intent background processing started")
            return True
        except Exception as e:
            logger.error(f"Failed to start intent background processing: {e}")
            self.active = False
            return False
    
    def stop_background_processing(self):
        """Stop the background processing thread."""
        if not self.active:
            return True
        
        self.active = False
        if self.background_thread:
            self.background_thread.join(timeout=2)
        logger.info("Intent background processing stopped")
        return True
    
    def _background_loop(self):
        """Background loop for intent processing and task execution."""
        logger.info("Intent background processing loop started")
        
        while self.active:
            try:
                # Check for tasks due for execution
                self._process_task_queue()
                
                # Check for recurring tasks based on time or patterns
                self._check_recurring_tasks()
                
                # Analyze behavior patterns to identify new routines
                self._analyze_behavior_patterns()
                
                # Save state periodically
                if random.random() < 0.1:  # 10% chance each cycle to save (to avoid excessive writes)
                    self.save_intent_data()
                
                # Sleep before next cycle
                time.sleep(10)  # Check every 10 seconds
            
            except Exception as e:
                logger.error(f"Error in intent background loop: {e}")
                time.sleep(60)  # Wait before retrying if there was an error
    
    def _process_task_queue(self):
        """Process and execute tasks from the queue."""
        now = datetime.now()
        tasks_to_remove = []
        
        for i, task in enumerate(self.task_queue):
            # Check if task is due for execution
            if "scheduled_time" in task:
                scheduled_time = datetime.fromisoformat(task["scheduled_time"])
                if now >= scheduled_time:
                    # Execute the task
                    success = self._execute_task(task)
                    if success or task.get("remove_on_failure", True):
                        tasks_to_remove.append(i)
            else:
                # Tasks without a scheduled time are executed immediately
                success = self._execute_task(task)
                if success or task.get("remove_on_failure", True):
                    tasks_to_remove.append(i)
        
        # Remove executed tasks in reverse order to avoid index issues
        for i in sorted(tasks_to_remove, reverse=True):
            del self.task_queue[i]
    
    def _execute_task(self, task):
        """Execute a specific task."""
        task_type = task.get("type", "unknown")
        logger.info(f"Executing task: {task_type}")
        
        try:
            # Record task execution in behavior history
            self._record_behavior({
                "type": "task_execution",
                "task": task,
                "timestamp": datetime.now().isoformat()
            })
            
            # This would be implemented to handle various task types
            # For now, we'll just log what would happen
            
            if task_type == "reminder":
                logger.info(f"REMINDER: {task.get('content', 'No content')}")
                # In a real system, this would trigger a notification
                
            elif task_type == "data_collection":
                logger.info(f"Collecting data for: {task.get('target', 'Unknown')}")
                # This would connect to data collection systems
                
            elif task_type == "message":
                logger.info(f"Sending message: {task.get('content', 'No content')}")
                # This would connect to messaging systems
                
            elif task_type == "system_task":
                logger.info(f"Running system task: {task.get('action', 'Unknown')}")
                # This would perform system maintenance tasks
                
            elif task_type == "content_preparation":
                logger.info(f"Preparing content: {task.get('description', 'Unknown')}")
                # This would prepare content for the user
                
            logger.info(f"Task '{task_type}' executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing task {task_type}: {e}")
            return False
    
    def _check_recurring_tasks(self):
        """Check and queue recurring tasks based on their schedule."""
        now = datetime.now()
        
        for task in self.recurring_tasks:
            # Skip if task is inactive
            if not task.get("active", True):
                continue
                
            # Get the last execution time
            last_execution = None
            if "last_execution" in task:
                last_execution = datetime.fromisoformat(task["last_execution"])
            
            # Check if it's time to execute based on the pattern
            should_execute = False
            
            if "interval_hours" in task:
                # Time-based recurrence
                interval = timedelta(hours=task["interval_hours"])
                if last_execution is None or (now - last_execution) >= interval:
                    should_execute = True
            
            elif "day_of_week" in task:
                # Weekly recurrence
                target_day = task["day_of_week"]  # 0 = Monday, 6 = Sunday
                if now.weekday() == target_day:
                    # Check if it was already executed today
                    if (last_execution is None or 
                        last_execution.date() != now.date()):
                        if "hour_of_day" in task:
                            # Execute at specific hour
                            if now.hour == task["hour_of_day"]:
                                should_execute = True
                        else:
                            should_execute = True
            
            elif "trigger_pattern" in task:
                # Pattern-based recurrence
                # This would check for specific user behavior patterns
                # For simplicity, we'll randomly trigger pattern-based tasks
                if random.random() < 0.05:  # 5% chance to trigger
                    should_execute = True
            
            # Queue the task if it should be executed
            if should_execute:
                # Create a copy of the task for the queue
                queue_task = task.copy()
                queue_task["scheduled_time"] = now.isoformat()
                self.task_queue.append(queue_task)
                
                # Update last execution time
                task["last_execution"] = now.isoformat()
    
    def _analyze_behavior_patterns(self):
        """Analyze user behavior to identify patterns and routines."""
        # This would implement sophisticated pattern recognition
        # For this example, we'll use a simplified approach
        
        # Only analyze periodically (every ~hour in our simulation)
        if random.random() > 0.017:  # ~1.7% chance each 10s cycle = ~1/hour
            return
        
        logger.info("Analyzing behavior patterns")
        
        # Get recent behavior
        recent_behavior = self.behavior_history[-50:]  # Last 50 behaviors
        
        # Look for time-based patterns (simplified)
        time_patterns = self._find_time_patterns(recent_behavior)
        
        # Look for sequential patterns (simplified)
        sequence_patterns = self._find_sequence_patterns(recent_behavior)
        
        # Update intent patterns
        for pattern in time_patterns + sequence_patterns:
            pattern_id = f"pattern_{len(self.intent_patterns) + 1}"
            self.intent_patterns[pattern_id] = {
                "type": pattern["type"],
                "confidence": pattern["confidence"],
                "description": pattern["description"],
                "identified": datetime.now().isoformat(),
                "pattern_data": pattern["data"]
            }
        
        if time_patterns or sequence_patterns:
            logger.info(f"Identified {len(time_patterns) + len(sequence_patterns)} new behavior patterns")
            self.save_intent_data()
    
    def _find_time_patterns(self, behaviors):
        """Find patterns based on time of day or day of week."""
        # This would implement proper time-based pattern recognition
        # For this example, we'll simulate finding a pattern
        
        # Simulate finding a morning routine pattern
        if random.random() < 0.2:  # 20% chance to find a pattern
            return [{
                "type": "time_pattern",
                "confidence": 0.75,
                "description": "Morning information check routine",
                "data": {
                    "day_period": "morning",
                    "time_range": [6, 9],
                    "actions": ["check_weather", "check_calendar", "check_news"]
                }
            }]
        return []
    
    def _find_sequence_patterns(self, behaviors):
        """Find patterns in sequences of user behaviors."""
        # This would implement proper sequence pattern recognition
        # For this example, we'll simulate finding a pattern
        
        # Simulate finding a sequence pattern
        if random.random() < 0.2:  # 20% chance to find a pattern
            return [{
                "type": "sequence_pattern",
                "confidence": 0.8,
                "description": "Project research sequence",
                "data": {
                    "trigger": "research_start",
                    "sequence": ["web_search", "document_creation", "bookmark_saving"]
                }
            }]
        return []
    
    def process_input(self, input_data):
        """Process user input to recognize intent and take appropriate action."""
        # Add to behavior history
        self._record_behavior({
            "type": "user_input",
            "data": input_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract text and context from input
        text = input_data.get("text", "")
        context = input_data.get("context", {})
        
        # Recognize intent
        intent = self._recognize_intent(text, context)
        
        # Take action based on intent
        response = self._respond_to_intent(intent, input_data)
        
        return response
    
    def _recognize_intent(self, text, context=None):
        """Recognize the user's intent from input text and context."""
        # This would implement proper intent recognition with NLP
        # For this example, we'll use simple pattern matching
        
        intent = {
            "primary": "unknown",
            "confidence": 0.5,
            "entities": {},
            "context": context or {}
        }
        
        # Simple pattern matching examples
        if re.search(r'\b(remind|reminder|remember)\b', text.lower()):
            intent["primary"] = "reminder"
            intent["confidence"] = 0.8
            # Extract time entity if present
            time_match = re.search(r'at (\d+[:\d]*\s*[ap]\.?m\.?)', text.lower())
            if time_match:
                intent["entities"]["time"] = time_match.group(1)
        
        elif re.search(r'\b(schedule|appointment|meeting|calendar)\b', text.lower()):
            intent["primary"] = "calendar"
            intent["confidence"] = 0.75
            # Extract date entity if present
            date_match = re.search(r'on ([a-zA-Z]+ \d+)', text.lower())
            if date_match:
                intent["entities"]["date"] = date_match.group(1)
        
        elif re.search(r'\b(search|find|look up)\b', text.lower()):
            intent["primary"] = "search"
            intent["confidence"] = 0.7
            # Extract query entity
            query_match = re.search(r'(search|find|look up)\s+(?:for\s+)?(.+)', text.lower())
            if query_match:
                intent["entities"]["query"] = query_match.group(2)
        
        elif re.search(r'\b(send|message|text|call)\b', text.lower()):
            intent["primary"] = "communication"
            intent["confidence"] = 0.8
            # Extract recipient entity if present
            recipient_match = re.search(r'to\s+([a-zA-Z]+)', text.lower())
            if recipient_match:
                intent["entities"]["recipient"] = recipient_match.group(1)
        
        elif re.search(r'\b(help|explain|how do|how to)\b', text.lower()):
            intent["primary"] = "help"
            intent["confidence"] = 0.9
        
        # Apply context to refine intent
        if context:
            self._refine_intent_with_context(intent, context)
        
        logger.debug(f"Recognized intent: {intent['primary']} (confidence: {intent['confidence']})")
        return intent
    
    def _refine_intent_with_context(self, intent, context):
        """Refine the recognized intent using contextual information."""
        # Adjust confidence based on context
        
        # If in a messaging app, boost confidence of communication intent
        if context.get("app") == "messaging" and intent["primary"] == "communication":
            intent["confidence"] = min(1.0, intent["confidence"] + 0.1)
        
        # If a reminder was recognized but we're in a calendar app, adjust to calendar intent
        if context.get("app") == "calendar" and intent["primary"] == "reminder":
            intent["primary"] = "calendar"
            intent["confidence"] = min(1.0, intent["confidence"] + 0.05)
        
        # Use location context to enhance intents
        if "location" in context:
            if context["location"] == "home" and intent["primary"] == "reminder":
                intent["entities"]["location"] = "home"
        
        # Use time context
        if "time" in context:
            current_hour = context["time"].get("hour", 0)
            
            # Morning routine detection
            if 5 <= current_hour <= 9 and intent["primary"] == "unknown":
                intent["primary"] = "morning_routine"
                intent["confidence"] = 0.6
    
    def _respond_to_intent(self, intent, original_input):
        """Generate a response based on the recognized intent."""
        response = {
            "text": "I understand your request.",
            "intent": intent["primary"],
            "actions": []
        }
        
        # Take actions based on intent
        if intent["primary"] == "reminder" and intent["confidence"] > 0.7:
            # Create a reminder task
            reminder_task = {
                "type": "reminder",
                "content": original_input.get("text", "Reminder"),
                "created": datetime.now().isoformat()
            }
            
            # Add scheduled time if available
            if "time" in intent["entities"]:
                # This would properly parse the time in a real implementation
                scheduled_time = datetime.now() + timedelta(hours=1)  # Placeholder
                reminder_task["scheduled_time"] = scheduled_time.isoformat()
            
            # Add to task queue
            self.task_queue.append(reminder_task)
            response["text"] = "I've set a reminder for you."
            response["actions"].append({"type": "reminder_created", "task": reminder_task})
        
        elif intent["primary"] == "calendar" and intent["confidence"] > 0.7:
            # Simulate calendar event creation
            response["text"] = "I can help you with your calendar."
            response["actions"].append({"type": "calendar_access"})
        
        elif intent["primary"] == "search" and intent["confidence"] > 0.6:
            # Simulate search action
            query = intent["entities"].get("query", "")
            response["text"] = f"I'll search for information about {query}."
            response["actions"].append({"type": "search", "query": query})
        
        elif intent["primary"] == "communication" and intent["confidence"] > 0.7:
            # Simulate communication action
            recipient = intent["entities"].get("recipient", "someone")
            response["text"] = f"I can help you communicate with {recipient}."
            response["actions"].append({"type": "communication_preparation", "recipient": recipient})
        
        elif intent["primary"] == "help":
            # Provide help information
            response["text"] = "I'm here to help you. You can ask me to set reminders, search for information, help with communication, and more."
            response["actions"].append({"type": "help_provided"})
        
        elif intent["primary"] == "morning_routine":
            # Trigger morning routine
            response["text"] = "Good morning! I'm preparing your daily briefing."
            response["actions"].append({"type": "routine_triggered", "routine": "morning"})
        
        # Save the interaction to history
        self._record_behavior({
            "type": "system_response",
            "intent": intent["primary"],
            "confidence": intent["confidence"],
            "actions": response["actions"],
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def add_task(self, task_data):
        """Add a task to the queue, either for immediate or scheduled execution."""
        try:
            # Validate required task fields
            if "type" not in task_data:
                logger.error("Cannot add task: missing task type")
                return False
            
            # Add creation timestamp
            task_data["created"] = datetime.now().isoformat()
            
            # Add to task queue
            self.task_queue.append(task_data)
            logger.info(f"Added {task_data['type']} task to queue")
            
            # Save updated task queue
            self.save_intent_data()
            
            return True
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return False
    
    def add_recurring_task(self, task_data):
        """Add a recurring task that will be executed on a schedule."""
        try:
            # Validate required task fields
            if "type" not in task_data:
                logger.error("Cannot add recurring task: missing task type")
                return False
            
            # Validate that it has a recurrence pattern
            if not any(key in task_data for key in ["interval_hours", "day_of_week", "trigger_pattern"]):
                logger.error("Cannot add recurring task: missing recurrence pattern")
                return False
            
            # Add creation timestamp
            task_data["created"] = datetime.now().isoformat()
            task_data["active"] = True
            
            # Add to recurring tasks
            self.recurring_tasks.append(task_data)
            logger.info(f"Added recurring {task_data['type']} task")
            
            # Save updated task data
            self.save_intent_data()
            
            return True
        except Exception as e:
            logger.error(f"Error adding recurring task: {e}")
            return False
    
    def remove_task(self, task_id):
        """Remove a task from the queue by its ID."""
        try:
            # In a real implementation, tasks would have unique IDs
            # For this example, we'll use the index as the ID
            if 0 <= task_id < len(self.task_queue):
                removed_task = self.task_queue.pop(task_id)
                logger.info(f"Removed task {task_id} from queue")
                self.save_intent_data()
                return True
            else:
                logger.error(f"Task ID {task_id} not found in queue")
                return False
        except Exception as e:
            logger.error(f"Error removing task: {e}")
            return False
    
    def _record_behavior(self, behavior_data):
        """Record a user or system behavior for pattern analysis."""
        self.behavior_history.append(behavior_data)
        
        # Keep history size manageable
        if len(self.behavior_history) > 200:
            self.behavior_history = self.behavior_history[-200:]
    
    def predict_next_action(self, context=None):
        """Predict what the user might want to do next based on patterns."""
        try:
            # This would implement proper prediction using the learned patterns
            # For this example, we'll use a simplified approach
            
            now = datetime.now()
            predictions = []
            
            # Check for active time-based patterns
            for pattern_id, pattern in self.intent_patterns.items():
                if pattern["type"] == "time_pattern":
                    pattern_data = pattern["pattern_data"]
                    
                    # Check if current time matches the pattern
                    if "day_period" in pattern_data and pattern_data["day_period"] == "morning":
                        if 6 <= now.hour <= 9:
                            predictions.append({
                                "action": "morning_routine",
                                "confidence": pattern["confidence"],
                                "source_pattern": pattern_id,
                                "description": pattern["description"]
                            })
                    
                    # Other time periods would be checked here
            
            # Return the highest confidence prediction if any
            if predictions:
                best_prediction = max(predictions, key=lambda p: p["confidence"])
                if best_prediction["confidence"] >= self.thresholds["prediction"]:
                    logger.info(f"Predicted next action: {best_prediction['action']}")
                    return best_prediction
            
            # Default prediction
            return {
                "action": "no_specific_prediction",
                "confidence": 0.3,
                "source": "default",
                "description": "No strong prediction available"
            }
        
        except Exception as e:
            logger.error(f"Error predicting next action: {e}")
            return {
                "action": "prediction_error",
                "confidence": 0,
                "source": "error",
                "description": "Error during prediction"
            }
    
    def get_task_suggestions(self, context=None):
        """Get task suggestions based on current context and patterns."""
        try:
            now = datetime.now()
            suggestions = []
            
            # Simple time-based suggestions
            hour = now.hour
            weekday = now.weekday()  # 0 = Monday, 6 = Sunday
            
            # Morning suggestions
            if 6 <= hour <= 9:
                suggestions.append({
                    "task": "Check today's weather",
                    "confidence": 0.7,
                    "type": "information"
                })
                
                suggestions.append({
                    "task": "Review calendar for today",
                    "confidence": 0.75,
                    "type": "productivity"
                })
            
            # Evening suggestions
            elif 17 <= hour <= 22:
                suggestions.append({
                    "task": "Review tomorrow's schedule",
                    "confidence": 0.65,
                    "type": "planning"
                })
            
            # Weekend suggestions
            if weekday >= 5:  # Saturday or Sunday
                suggestions.append({
                    "task": "Check entertainment options",
                    "confidence": 0.6,
                    "type": "leisure"
                })
            
            # Filter by confidence threshold
            return [s for s in suggestions if s["confidence"] >= self.thresholds["suggestion"]]
        
        except Exception as e:
            logger.error(f"Error generating task suggestions: {e}")
            return []
    
    def get_pending_tasks(self):
        """Get all pending tasks in the queue."""
        return self.task_queue
    
    def get_recurring_tasks(self):
        """Get all recurring tasks."""
        return self.recurring_tasks
