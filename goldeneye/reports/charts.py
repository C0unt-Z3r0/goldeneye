"""
goldeneye/reports/charts.py
Gera graficos para os relatorios.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np


def generate_risk_chart(output_path: Path, vuln_counts: dict = None):
    """Gera grafico de pizza com severidade das vulnerabilidades."""
    
    if not vuln_counts:
        vuln_counts = {"Crítico": 0, "Alto": 1, "Médio": 3, "Baixo": 5, "Info": 9}
    
    labels = list(vuln_counts.keys())
    sizes = list(vuln_counts.values())
    colors = ['#DC143C', '#FF4500', '#FFA500', '#228B22', '#666666']
    explode = (0.1, 0.05, 0, 0, 0)
    
    fig, ax = plt.subplots(figsize=(6, 4))
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.0f%%', shadow=False, startangle=90,
    )
    
    for t in autotexts:
        t.set_color('white')
        t.set_fontsize(9)
    
    ax.set_title('Vulnerabilidades por Severidade', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_score_gauge(output_path: Path, score: float = 7.5):
    """Gera medidor de risco."""
    
    fig, ax = plt.subplots(figsize=(4, 1.5))
    
    colors = ['#228B22', '#228B22', '#FFA500', '#FFA500', '#FF4500', '#FF4500', '#DC143C', '#DC143C', '#DC143C', '#DC143C']
    
    ax.barh(0, 10, color='#EEEEEE', height=0.4)
    
    for i in range(int(score)):
        ax.barh(0, 1, left=i, color=colors[i], height=0.4)
    
    ax.set_xlim(0, 10)
    ax.axis('off')
    ax.text(score + 0.1, 0, f'{score}/10', fontsize=14, fontweight='bold', va='center')
    ax.set_title('Score de Risco', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path
