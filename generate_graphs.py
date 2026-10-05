import matplotlib.pyplot as plt
import numpy as np

def plot_adaptive_engine_behavior():
    """Generates a graph showing QBER fluctuations triggering Gear changes."""
    # Simulate 20 messages over time
    messages = np.arange(1, 21)
    
    # Simulate a dynamic channel: Stable -> Eavesdropper (Eve) -> Network Failure -> Stable
    qber_values = [0.03, 0.04, 0.05, 0.06, 0.12, 0.14, 0.15, 0.08, 0.04, 0.05, 
                   0.03, 0.04, 0.02, 0.03, 0.04, 0.03, 0.02, 0.04, 0.05, 0.03]
    
    # Simulate network availability (False at message 12-14 to force Gear 1)
    pqc_availability = [True]*11 + [False]*3 + [True]*6
    
    gears = []
    threshold = 0.11 # Cryptographically justified BB84 bound
    
    for qber, pqc in zip(qber_values, pqc_availability):
        if not pqc:
            gears.append(1) # Gear 1: Classical ECDH
        elif qber > threshold:
            gears.append(2) # Gear 2: Post-Quantum ML-KEM
        else:
            gears.append(3) # Gear 3: QKD + ML-KEM
            
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Plot QBER
    color = 'tab:red'
    ax1.set_xlabel('Message Sequence (Time)')
    ax1.set_ylabel('Quantum Bit Error Rate (QBER)', color=color)
    ax1.plot(messages, qber_values, color=color, marker='o', label="Measured QBER")
    ax1.axhline(y=threshold, color='black', linestyle='--', label="11% Security Threshold")
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(0, 0.20)
    
    # Annotate the Eavesdropping Event
    ax1.annotate('Active Eavesdropping\nDetected', xy=(6, 0.14), xytext=(2, 0.16),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))

    # Plot Active Gear on secondary Y-axis
    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Active Security Gear', color=color)  
    ax2.step(messages, gears, color=color, where='mid', linewidth=2, label="Active Gear")
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_yticks([1, 2, 3])
    ax2.set_yticklabels(['Gear 1 (Classical)', 'Gear 2 (PQC)', 'Gear 3 (Hybrid)'])
    
    # Annotate the Network Failure Event
    ax2.annotate('Network Constraint\n(PQC Unavailable)', xy=(13, 1), xytext=(12, 1.5),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))

    fig.tight_layout()
    plt.title("Adaptive Security Model: Dynamic Gear Transitions based on Channel Health")
    plt.grid(True, alpha=0.3)
    plt.savefig("adaptive_gear_transitions.png", dpi=300)
    print("Saved: adaptive_gear_transitions.png")

def plot_bandwidth_overhead():
    """Generates a bar chart comparing payload sizes to justify Gear 1 fallbacks."""
    mechanisms = ['Classical ECDH\n(secp384r1)', 'Post-Quantum\nML-KEM-512', 'Post-Quantum\nML-DSA-44']
    sizes_bytes = [97, 800, 2420] # Standard byte sizes for these specific parameter sets
    
    plt.figure(figsize=(8, 5))
    bars = plt.bar(mechanisms, sizes_bytes, color=['#2ca02c', '#ff7f0e', '#1f77b4'])
    plt.ylabel('Payload Size (Bytes)')
    plt.title('Communication Overhead: Classical vs Post-Quantum')
    plt.yscale('log') # Log scale visually explains network fragmentation risks
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (yval*0.1), f'{yval} B', ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig("bandwidth_overhead.png", dpi=300)
    print("Saved: bandwidth_overhead.png")

if __name__ == "__main__":
    plot_adaptive_engine_behavior()
    plot_bandwidth_overhead()