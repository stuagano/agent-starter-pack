import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class GherkinFeedback:
    def __init__(self):
        self.feedback_file = Path("feedback/gherkin_feedback.json")
        self.feedback_file.parent.mkdir(exist_ok=True)
        self.load_feedback()
    
    def load_feedback(self):
        """Load existing feedback from file."""
        try:
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r') as f:
                    self.feedback_data = json.load(f)
            else:
                self.feedback_data = {
                    "feedback_entries": [],
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0.0"
                    }
                }
        except Exception as e:
            st.error(f"Failed to load feedback: {e}")
            self.feedback_data = {
                "feedback_entries": [],
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }
    
    def save_feedback(self):
        """Save feedback to file."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Failed to save feedback: {e}")
            return False
    
    def parse_gherkin(self, gherkin_text: str) -> Dict[str, Any]:
        """Parse Gherkin text into structured data."""
        lines = gherkin_text.strip().split('\n')
        parsed = {
            "feature": "",
            "scenario": "",
            "given": [],
            "when": [],
            "then": [],
            "and": [],
            "but": [],
            "comments": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Feature:'):
                parsed["feature"] = line.replace('Feature:', '').strip()
            elif line.startswith('Scenario:'):
                parsed["scenario"] = line.replace('Scenario:', '').strip()
            elif line.startswith('Given '):
                parsed["given"].append(line.replace('Given ', '').strip())
                current_section = "given"
            elif line.startswith('When '):
                parsed["when"].append(line.replace('When ', '').strip())
                current_section = "when"
            elif line.startswith('Then '):
                parsed["then"].append(line.replace('Then ', '').strip())
                current_section = "then"
            elif line.startswith('And '):
                if current_section:
                    parsed["and"].append({
                        "section": current_section,
                        "text": line.replace('And ', '').strip()
                    })
            elif line.startswith('But '):
                if current_section:
                    parsed["but"].append({
                        "section": current_section,
                        "text": line.replace('But ', '').strip()
                    })
            elif line.startswith('#'):
                parsed["comments"].append(line.replace('#', '').strip())
        
        return parsed
    
    def add_feedback_entry(self, gherkin_text: str, category: str, priority: str, status: str):
        """Add a new feedback entry."""
        parsed = self.parse_gherkin(gherkin_text)
        
        entry = {
            "id": f"feedback_{len(self.feedback_data['feedback_entries']) + 1}",
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "priority": priority,
            "status": status,
            "gherkin_text": gherkin_text,
            "parsed": parsed
        }
        
        self.feedback_data["feedback_entries"].append(entry)
        return self.save_feedback()
    
    def render_feedback_page(self):
        """Render the Gherkin feedback interface."""
        st.title("📝 Gherkin Feedback Interface")
        st.markdown("Provide feedback in natural language using Gherkin syntax.")
        
        # Feedback input section
        st.header("✍️ Submit Feedback")
        
        # Category selection
        category = st.selectbox(
            "Feedback Category",
            ["Bug Report", "Feature Request", "Usability Issue", "Performance", "Documentation", "Other"],
            help="Select the type of feedback you're providing"
        )
        
        # Priority selection
        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High", "Critical"],
            help="How important is this feedback?"
        )
        
        # Status selection
        status = st.selectbox(
            "Status",
            ["New", "In Progress", "Resolved", "Won't Fix"],
            help="Current status of this feedback"
        )
        
        # Gherkin text input
        st.subheader("🎯 Gherkin Feedback")
        st.markdown("""
        **Gherkin Syntax Guide:**
        - `Feature:` - What feature you're testing
        - `Scenario:` - Specific scenario being tested
        - `Given` - Preconditions or setup
        - `When` - Actions taken
        - `Then` - Expected outcomes
        - `And` - Additional conditions or outcomes
        - `But` - Negative conditions or outcomes
        - `#` - Comments (optional)
        """)
        
        # Example template
        with st.expander("📋 Example Template"):
            st.code("""
Feature: PDF Upload and Processing
Scenario: User uploads a PDF and asks questions
  Given I am on the PDF Upload page
  And I have a valid PDF file
  When I upload the PDF file
  And I wait for processing to complete
  And I ask "What is the main topic?"
  Then I should see a relevant answer
  And the answer should reference the PDF content
  But I should not see placeholder text
            """, language="gherkin")
        
        # Text area for Gherkin input
        gherkin_text = st.text_area(
            "Enter your feedback in Gherkin format:",
            height=300,
            placeholder="""Feature: [Feature Name]
Scenario: [Scenario Description]
  Given [precondition]
  When [action]
  Then [expected outcome]
  And [additional outcome]
  But [negative outcome]
# Additional comments here""",
            help="Write your feedback using Gherkin syntax"
        )
        
        # Submit button
        if st.button("📤 Submit Feedback"):
            if gherkin_text.strip():
                if self.add_feedback_entry(gherkin_text, category, priority, status):
                    st.success("✅ Feedback submitted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save feedback")
            else:
                st.warning("⚠️ Please enter feedback text")
        
        st.divider()
        
        # Feedback history
        st.header("📚 Feedback History")
        
        if not self.feedback_data["feedback_entries"]:
            st.info("No feedback submitted yet. Be the first to provide feedback!")
        else:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_category = st.selectbox(
                    "Filter by Category",
                    ["All"] + list(set(entry["category"] for entry in self.feedback_data["feedback_entries"]))
                )
            with col2:
                filter_priority = st.selectbox(
                    "Filter by Priority",
                    ["All"] + list(set(entry["priority"] for entry in self.feedback_data["feedback_entries"]))
                )
            with col3:
                filter_status = st.selectbox(
                    "Filter by Status",
                    ["All"] + list(set(entry["status"] for entry in self.feedback_data["feedback_entries"]))
                )
            
            # Filter entries
            filtered_entries = self.feedback_data["feedback_entries"]
            if filter_category != "All":
                filtered_entries = [e for e in filtered_entries if e["category"] == filter_category]
            if filter_priority != "All":
                filtered_entries = [e for e in filtered_entries if e["priority"] == filter_priority]
            if filter_status != "All":
                filtered_entries = [e for e in filtered_entries if e["status"] == filter_status]
            
            # Display entries
            for entry in reversed(filtered_entries):  # Show newest first
                with st.expander(f"📝 {entry['parsed']['feature']} - {entry['category']} ({entry['priority']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Scenario:** {entry['parsed']['scenario']}")
                        
                        if entry['parsed']['given']:
                            st.write("**Given:**")
                            for given in entry['parsed']['given']:
                                st.write(f"• {given}")
                        
                        if entry['parsed']['when']:
                            st.write("**When:**")
                            for when in entry['parsed']['when']:
                                st.write(f"• {when}")
                        
                        if entry['parsed']['then']:
                            st.write("**Then:**")
                            for then in entry['parsed']['then']:
                                st.write(f"• {then}")
                        
                        # Show And/But statements
                        for and_item in entry['parsed']['and']:
                            st.write(f"• **And:** {and_item['text']}")
                        
                        for but_item in entry['parsed']['but']:
                            st.write(f"• **But:** {but_item['text']}")
                        
                        if entry['parsed']['comments']:
                            st.write("**Comments:**")
                            for comment in entry['parsed']['comments']:
                                st.write(f"• {comment}")
                    
                    with col2:
                        st.write(f"**Category:** {entry['category']}")
                        st.write(f"**Priority:** {entry['priority']}")
                        st.write(f"**Status:** {entry['status']}")
                        st.write(f"**Date:** {entry['timestamp'][:10]}")
                        
                        # Status update
                        new_status = st.selectbox(
                            "Update Status",
                            ["New", "In Progress", "Resolved", "Won't Fix"],
                            index=["New", "In Progress", "Resolved", "Won't Fix"].index(entry['status']),
                            key=f"status_{entry['id']}"
                        )
                        
                        if new_status != entry['status']:
                            if st.button("Update", key=f"update_{entry['id']}"):
                                entry['status'] = new_status
                                if self.save_feedback():
                                    st.success("✅ Status updated!")
                                    st.rerun()
        
        # Export functionality
        st.divider()
        st.header("📤 Export Feedback")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export as JSON"):
                if self.feedback_data["feedback_entries"]:
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(self.feedback_data, indent=2),
                        file_name=f"gherkin_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No feedback to export")
        
        with col2:
            if st.button("📊 Export Summary"):
                if self.feedback_data["feedback_entries"]:
                    summary = self.generate_summary()
                    st.download_button(
                        label="Download Summary",
                        data=summary,
                        file_name=f"feedback_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.warning("No feedback to export")
    
    def generate_summary(self) -> str:
        """Generate a text summary of all feedback."""
        entries = self.feedback_data["feedback_entries"]
        
        summary = f"Penny Assistant Feedback Summary\n"
        summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"Total Entries: {len(entries)}\n\n"
        
        # Category breakdown
        categories = {}
        priorities = {}
        statuses = {}
        
        for entry in entries:
            categories[entry['category']] = categories.get(entry['category'], 0) + 1
            priorities[entry['priority']] = priorities.get(entry['priority'], 0) + 1
            statuses[entry['status']] = statuses.get(entry['status'], 0) + 1
        
        summary += "Category Breakdown:\n"
        for category, count in categories.items():
            summary += f"  {category}: {count}\n"
        
        summary += "\nPriority Breakdown:\n"
        for priority, count in priorities.items():
            summary += f"  {priority}: {count}\n"
        
        summary += "\nStatus Breakdown:\n"
        for status, count in statuses.items():
            summary += f"  {status}: {count}\n"
        
        summary += "\nDetailed Entries:\n"
        summary += "=" * 50 + "\n"
        
        for entry in entries:
            summary += f"\nID: {entry['id']}\n"
            summary += f"Date: {entry['timestamp'][:10]}\n"
            summary += f"Category: {entry['category']}\n"
            summary += f"Priority: {entry['priority']}\n"
            summary += f"Status: {entry['status']}\n"
            summary += f"Feature: {entry['parsed']['feature']}\n"
            summary += f"Scenario: {entry['parsed']['scenario']}\n"
            summary += f"Gherkin Text:\n{entry['gherkin_text']}\n"
            summary += "-" * 30 + "\n"
        
        return summary

# Global instance
gherkin_feedback = GherkinFeedback() 