# qrft_chat.py
"""
QRFT Deterministic Agent CLI
No-LLM symbolic reasoning with QRFT control
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import json
import time
from typing import Dict, Any
from qrft_agent_integrated import create_integrated_agent, IntegratedQRFTAgent

class QRFTChatInterface:
    """Command-line interface for QRFT agent"""
    
    def __init__(self):
        self.agent = create_integrated_agent()
        self.session_active = True
        self.debug_mode = False
        
        # Commands
        self.commands = {
            '/help': self.show_help,
            '/state': self.show_state,
            '/debug': self.toggle_debug,
            '/log': self.save_log,
            '/reset': self.reset_agent,
            '/signals': self.show_signals,
            '/facts': self.show_facts,
            '/gaps': self.show_gaps,
            '/contradictions': self.show_contradictions,
            '/quit': self.quit_session
        }
        
    def run(self):
        """Main chat loop"""
        print("QRFT Deterministic Agent - No LLM Symbolic Reasoning")
        print("=" * 60)
        print("Type /help for commands or ask questions")
        print("Mathematical queries: solve x^2 - 5x + 6 = 0")
        print("Information queries: what is kinetic energy?")
        print("=" * 60)
        
        while self.session_active:
            try:
                user_input = input("\n🧠 QRFT> ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                    continue
                    
                # Process with agent
                start_time = time.time()
                response = self.agent.process_input(user_input)
                duration = time.time() - start_time
                
                # Display response
                print(f"\n🤖 Agent: {response}")
                
                # Show debug info if enabled
                if self.debug_mode:
                    self.show_debug_info(duration)
                    
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Type /quit to exit properly.")
            except Exception as e:
                print(f"\nError: {e}")
                
    def handle_command(self, command: str):
        """Handle user commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd in self.commands:
            self.commands[cmd]()
        else:
            print(f"Unknown command: {cmd}. Type /help for available commands.")
            
    def show_help(self):
        """Show help information"""
        help_text = """
QRFT Agent Commands:
  /help         - Show this help
  /state        - Show complete agent state
  /signals      - Show current QRFT signals (X_G, X_F, X_T)
  /facts        - Show all facts in knowledge base
  /gaps         - Show knowledge gaps
  /contradictions - Show detected contradictions
  /debug        - Toggle debug mode
  /log          - Save conversation log
  /reset        - Reset agent state
  /quit         - Exit chat

Example Queries:
  Mathematical: "solve x^2 - 4 = 0"
  Information: "what is Newton's first law?"
  Logical: "if all birds fly and penguins are birds, do penguins fly?"
  
The agent uses:
  • BM25 retrieval for knowledge lookup
  • SymPy for mathematical computation  
  • Paraconsistent logic for handling contradictions
  • QRFT signals for autonomous reasoning control
        """
        print(help_text)
        
    def show_state(self):
        """Show complete agent state"""
        state_summary = self.agent.get_state_summary()
        
        print("\n=== AGENT STATE ===")
        print(f"Session: {state_summary['state']['session_id'][:8]}...")
        print(f"Steps: {state_summary['state']['step_count']}")
        print(f"Facts: {state_summary['state']['facts_count']}")
        print(f"Gaps: {state_summary['state']['gaps_count']}")
        print(f"Contradictions: {state_summary['state']['contradictions_count']}")
        print(f"Last action: {state_summary['state']['last_action']}")
        
        print(f"\nQRFT Signals:")
        print(f"  X_G (contradiction): {state_summary['signals']['X_G']:.3f}")
        print(f"  X_F (gaps): {state_summary['signals']['X_F']:.3f}")
        print(f"  X_T (view mismatch): {state_summary['signals']['X_T']:.3f}")
        
    def show_signals(self):
        """Show current QRFT control signals"""
        signals = self.agent.signals
        
        print(f"\n=== QRFT CONTROL SIGNALS ===")
        print(f"X_G (Contradiction): {signals.X_G:.3f}")
        print(f"X_F (Gap/Novelty): {signals.X_F:.3f}")
        print(f"X_T (View Mismatch): {signals.X_T:.3f}")
        print(f"Last Update: {time.ctime(signals.last_update)}")
        
        # Signal interpretation
        tau_G = self.agent.policy.tau_G
        tau_F = self.agent.policy.tau_F  
        tau_T = self.agent.policy.tau_T
        
        print(f"\nThresholds: G={tau_G}, F={tau_F}, T={tau_T}")
        
        triggers = []
        if signals.X_G > tau_G:
            triggers.append("Glitchon (contradiction detection)")
        if signals.X_F > tau_F:
            triggers.append("Lacunon (gap filling)")
        if signals.X_T > tau_T:
            triggers.append("Tesseracton (view shift)")
            
        if triggers:
            print(f"Active triggers: {', '.join(triggers)}")
        else:
            print("No active triggers - normal operation")
            
    def show_facts(self):
        """Show all facts in knowledge base"""
        facts = self.agent.state.facts
        
        print(f"\n=== FACTS ({len(facts)}) ===")
        
        if not facts:
            print("No facts stored.")
            return
            
        # Group by source
        by_source = {}
        for fact in facts:
            if fact.source not in by_source:
                by_source[fact.source] = []
            by_source[fact.source].append(fact)
            
        for source, fact_list in by_source.items():
            print(f"\nFrom {source}:")
            for fact in fact_list[:5]:  # Show first 5
                print(f"  {fact}")
            if len(fact_list) > 5:
                print(f"  ... and {len(fact_list) - 5} more")
                
    def show_gaps(self):
        """Show knowledge gaps"""
        gaps = self.agent.state.gaps
        
        print(f"\n=== KNOWLEDGE GAPS ({len(gaps)}) ===")
        
        if not gaps:
            print("No knowledge gaps identified.")
            return
            
        for gap in list(gaps)[:10]:  # Show first 10
            print(f"  {gap.gap_type}: {gap.description}")
            if gap.context:
                print(f"    Context: {gap.context}")
                
    def show_contradictions(self):
        """Show detected contradictions"""
        contradictions = self.agent.state.get_contradictions()
        
        print(f"\n=== CONTRADICTIONS ({len(contradictions)}) ===")
        
        if not contradictions:
            print("No contradictions detected.")
            return
            
        for i, (fact1, fact2) in enumerate(contradictions[:5], 1):
            print(f"\n{i}. {fact1}")
            print(f"   contradicts")
            print(f"   {fact2}")
            print(f"   Sources: {fact1.source} vs {fact2.source}")
            
    def show_debug_info(self, duration: float):
        """Show debug information after each query"""
        print(f"\n--- DEBUG INFO ---")
        print(f"Processing time: {duration:.3f}s")
        
        signals = self.agent.signals
        print(f"Signals: G={signals.X_G:.3f}, F={signals.X_F:.3f}, T={signals.X_T:.3f}")
        
        state = self.agent.state
        print(f"State: {len(state.facts)} facts, {len(state.gaps)} gaps, {len(state.plan_steps)} plan steps")
        
        if state.get_pending_steps():
            print(f"Pending: {[s.action for s in state.get_pending_steps()]}")
            
    def toggle_debug(self):
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
        
    def save_log(self):
        """Save conversation log"""
        filename = f"qrft_chat_log_{int(time.time())}.json"
        self.agent.save_log(filename)
        print(f"Conversation log saved to: {filename}")
        
    def reset_agent(self):
        """Reset agent state"""
        confirm = input("Reset agent state? This will clear all facts and conversation history. (y/N): ")
        if confirm.lower() == 'y':
            self.agent = create_integrated_agent()
            print("Agent state reset.")
        else:
            print("Reset cancelled.")
            
    def quit_session(self):
        """Quit the chat session"""
        self.session_active = False
        print("Goodbye! 🧠")

def run_test_scenarios():
    """Run automated test scenarios"""
    print("Running QRFT Agent Test Scenarios...")
    print("=" * 50)
    
    agent = create_integrated_agent()
    
    test_queries = [
        # Mathematical queries
        "solve x^2 - 5x + 6 = 0",
        "what is the derivative of x^2?",
        "simplify (x+1)(x-1)",
        
        # Information retrieval
        "what is kinetic energy?",
        "explain Newton's first law",
        "what is modus ponens?",
        
        # Logical reasoning
        "if all birds fly and penguins are birds, do penguins fly?",
        "can something be both true and false?",
        
        # Gap detection
        "solve for y in the equation ax + by = c",
        "what is the speed of light in a vacuum?",
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        
        start_time = time.time()
        response = agent.process_input(query)
        duration = time.time() - start_time
        
        print(f"Response: {response}")
        print(f"Time: {duration:.3f}s")
        
        # Show signals
        signals = agent.signals
        print(f"Signals: G={signals.X_G:.3f}, F={signals.X_F:.3f}, T={signals.X_T:.3f}")
        
        results.append({
            'query': query,
            'response': response,
            'duration': duration,
            'signals': {
                'X_G': signals.X_G,
                'X_F': signals.X_F,
                'X_T': signals.X_T
            }
        })
        
        print("-" * 30)
        
    # Summary
    avg_time = sum(r['duration'] for r in results) / len(results)
    print(f"\nSummary:")
    print(f"  Processed {len(results)} queries")
    print(f"  Average response time: {avg_time:.3f}s")
    print(f"  Total facts learned: {len(agent.state.facts)}")
    print(f"  Knowledge gaps identified: {len(agent.state.gaps)}")
    print(f"  Contradictions found: {len(agent.state.get_contradictions())}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_test_scenarios()
    else:
        chat = QRFTChatInterface()
        chat.run()