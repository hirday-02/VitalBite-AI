"""
VitalBite AI — Emergency Alert Component
Displays high-visibility emergency red banner with Indian 112 emergency contact escalation.
"""
import streamlit as st
from typing import Dict, Any

def render_emergency_banner(eval_result: Dict[str, Any]):
    """Renders a prominent emergency alert box when high-risk symptoms are detected."""
    st.html(f"""
    <div class="emergency-overlay">
        <div style="font-size: 1.3rem; font-weight: 800; color: #DC2626; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.5rem;">
            🚨 POSSIBLE MEDICAL EMERGENCY DETECTED
        </div>
        <p style="font-weight: 700; margin-bottom: 0.5rem; color: #991B1B; font-size: 0.95rem;">
            These symptoms may require immediate medical evaluation. Do NOT rely on VitalBite AI for emergency care.
        </p>
        <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(239, 68, 68, 0.3); padding: 0.85rem 1.15rem; border-radius: 12px; margin-bottom: 0.85rem; color: #7F1D1D; font-size: 0.9rem;">
            <b style="color: #991B1B;">Immediate Recommended Actions:</b>
            <ul style="margin-top: 0.35rem; margin-bottom: 0.35rem; padding-left: 1.2rem; line-height: 1.5;">
                <li><b>CALL {eval_result.get('primary_number', '112')} NOW</b> (India Primary Emergency Contact)</li>
                <li>Proceed immediately to the nearest Emergency Department or Urgent Care Hospital</li>
                <li>Alert a family member, neighbor, or emergency contact nearby</li>
            </ul>
        </div>
        <p style="font-size: 0.82rem; color: #991B1B; margin: 0; font-weight: 500;">
            ⚠️ VitalBite AI is an educational assistant and cannot diagnose or treat medical emergencies.
        </p>
    </div>
    """)
