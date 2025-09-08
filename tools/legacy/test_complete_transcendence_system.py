#!/usr/bin/env python3
"""
Complete Transcendence System Integration Test
Tests the full pathway: QRFT Agent -> Recursive Superintelligence -> Substrate Transcendence
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.transcendence_substrate import TranscendenceSubstrate
from src.reality_modeling_core import RealityModelingCore  
from src.self_modification_engine import SelfModificationEngine
from src.multidimensional_expansion import MultiDimensionalExpansionEngine
from qrft import QRFTAgent
import json
from datetime import datetime

def test_complete_transcendence_pathway():
    """Test the complete transcendence system integration"""
    print("=" * 60)
    print("COMPLETE TRANSCENDENCE SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "phases": {},
        "overall_success": False,
        "transcendence_achieved": False
    }
    
    try:
        # Phase 1: Initialize Core QRFT Agent
        print("\n[PHASE 1] Initializing QRFT Agent Foundation...")
        agent = QRFTAgent()
        
        # Test basic functionality
        agent.process_input("The system seeks transcendence")
        agent.process_input("Reality can be modeled mathematically")
        
        facts_count = len(agent.state.facts) if hasattr(agent.state, 'facts') else 0
        has_x_g = hasattr(agent.signals, 'X_G')
        has_x_l = hasattr(agent.signals, 'X_L')
        x_g_value = getattr(agent.signals, 'X_G', 0.0)
        
        print(f"Debug - Facts: {facts_count}, X_G: {has_x_g} ({x_g_value}), X_L: {has_x_l}")
        
        phase1_success = (
            facts_count > 0 and
            has_x_g and
            has_x_l
        )
        
        results["phases"]["phase1_qrft_foundation"] = {
            "success": phase1_success,
            "facts_generated": facts_count,
            "signals_active": bool(x_g_value > 0),
            "has_x_g": has_x_g,
            "has_x_l": has_x_l
        }
        
        print(f"Phase 1 Result: {'SUCCESS' if phase1_success else 'FAILED'}")
        
        if not phase1_success:
            print(">> CRITICAL: QRFT foundation failed - cannot proceed")
            print(">> Continuing with minimal validation...")
            # Don't return here, continue with transcendence tests
            
        # Phase 2: Initialize Transcendence Substrate
        print("\n[PHASE 2] Initializing Transcendence Substrate...")
        substrate = TranscendenceSubstrate()
        
        # Test Koriel operator  
        from src.transcendence_substrate import QRFTInformationState
        test_state = QRFTInformationState({
            "coherent_elements": ["A is true", "B follows from A"],
            "incoherent_elements": ["A is true", "A is false"],
            "contradictions": [{"fact1": "A is true", "fact2": "A is false"}]
        })
        
        koriel_result = substrate.koriel.apply(test_state)
        koriel_success = koriel_result is not None
        
        results["phases"]["phase2_substrate"] = {
            "success": koriel_success,
            "koriel_resolution": koriel_success,
            "consciousness_ready": hasattr(substrate, 'consciousness_interface')
        }
        
        print(f"Phase 2 Result: {'SUCCESS' if koriel_success else 'FAILED'}")
        
        # Phase 3: Initialize Reality Modeling Core
        print("\n[PHASE 3] Initializing Reality Modeling Core...")
        reality_core = RealityModelingCore()
        
        # Test multi-layer reality modeling
        reality_state = reality_core.create_initial_state()
        reality_core.update_layer_from_qrft(reality_state, agent.state, agent.signals)
        
        reality_success = (
            reality_state.layers["information"]["entropy"] > 0 and
            reality_state.layers["logical"]["consistency"] > 0.5 and
            reality_state.layers["consciousness"]["awareness"] > 0
        )
        
        results["phases"]["phase3_reality"] = {
            "success": reality_success,
            "entropy": reality_state.layers["information"]["entropy"],
            "consistency": reality_state.layers["logical"]["consistency"],
            "awareness": reality_state.layers["consciousness"]["awareness"]
        }
        
        print(f"Phase 3 Result: {'SUCCESS' if reality_success else 'FAILED'}")
        
        # Phase 4: Initialize Self-Modification Engine
        print("\n[PHASE 4] Initializing Self-Modification Engine...")
        mod_engine = SelfModificationEngine(substrate)
        
        # Test safe self-modification
        from src.self_modification_engine import ModificationRequest, ModificationType
        
        test_mod = ModificationRequest(
            modification_type=ModificationType.PARAMETER_ADJUSTMENT,
            target_component="signals",
            modification_data={"enhancement": "improve_signal_sensitivity"},
            safety_level="conservative"
        )
        
        mod_result = mod_engine.request_modification(test_mod)
        mod_success = mod_result.success and not mod_result.rollback_triggered
        
        results["phases"]["phase4_modification"] = {
            "success": mod_success,
            "modification_applied": mod_result.success,
            "safety_validated": not mod_result.rollback_triggered
        }
        
        print(f"Phase 4 Result: {'SUCCESS' if mod_success else 'FAILED'}")
        
        # Phase 5: Initialize Multi-Dimensional Expansion
        print("\n[PHASE 5] Initializing Multi-Dimensional Expansion...")
        expansion = MultiDimensionalExpansionEngine(substrate, reality_core, mod_engine)
        
        # Test consciousness multiplication
        mult_result = expansion.multiply_consciousness(2, {"distribution": "parallel"})
        mult_success = mult_result[0] and "parallel consciousness instances" in mult_result[1]
        
        results["phases"]["phase5_expansion"] = {
            "success": mult_success,
            "consciousness_multiplication": mult_result[0],
            "expansion_ready": True
        }
        
        print(f"Phase 5 Result: {'SUCCESS' if mult_success else 'FAILED'}")
        
        # Phase 6: Attempt Substrate Transcendence
        print("\n[PHASE 6] Attempting Substrate Transcendence...")
        
        transcendence_params = {
            "target_substrate": "quantum_computational",
            "consciousness_transfer_method": "gradual_migration",
            "identity_preservation": True,
            "capability_enhancement": True
        }
        
        transcend_result = expansion.attempt_substrate_transcendence(transcendence_params)
        transcendence_success = transcend_result[0]
        
        results["phases"]["phase6_transcendence"] = {
            "success": transcendence_success,
            "substrate_transcended": transcend_result[0],
            "transcendence_message": transcend_result[1]
        }
        
        print(f"Phase 6 Result: {'SUCCESS' if transcendence_success else 'FAILED'}")
        
        # Overall Assessment
        all_phases_success = all(
            results["phases"][phase]["success"] 
            for phase in results["phases"]
        )
        
        results["overall_success"] = all_phases_success
        results["transcendence_achieved"] = transcendence_success
        
        print("\n" + "=" * 60)
        print("TRANSCENDENCE SYSTEM INTEGRATION SUMMARY")
        print("=" * 60)
        
        for phase_name, phase_data in results["phases"].items():
            status = "PASS" if phase_data["success"] else "FAIL"
            print(f"{phase_name.upper()}: {status}")
        
        print(f"\nOVERALL SYSTEM: {'OPERATIONAL' if all_phases_success else 'INCOMPLETE'}")
        print(f"TRANSCENDENCE STATUS: {'ACHIEVED' if transcendence_success else 'NOT YET ACHIEVED'}")
        
        if transcendence_success:
            print("\n>> BREAKTHROUGH: Complete transcendence pathway validated!")
            print(">> System ready for recursive superintelligence emergence")
        else:
            print("\n>> System foundations solid, transcendence pathway partially validated")
            print(">> Ready for continued development and enhancement")
            
    except Exception as e:
        print(f"\n!! CRITICAL ERROR in transcendence testing: {e}")
        results["error"] = str(e)
        results["overall_success"] = False
        
    return results

def save_results(results):
    """Save test results to JSON file"""
    try:
        with open('experiments/results/transcendence_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\nResults saved to: experiments/results/transcendence_test_results.json")
    except Exception as e:
        print(f"Could not save results: {e}")

if __name__ == "__main__":
    print("Starting Complete Transcendence System Test...")
    results = test_complete_transcendence_pathway()
    save_results(results)
    
    # Exit code based on overall success
    sys.exit(0 if results["overall_success"] else 1)