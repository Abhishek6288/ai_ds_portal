import plotly.graph_objects as go

def build_radar_performance_chart(categories, scores):
    """
    Generates a Plotly radar/polar chart representing student topic mastery.
    """
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.25)',  # Soft purple tint
        line=dict(color='#8b5cf6', width=2),     # Primary accent border
        marker=dict(size=6, color='#06b6d4')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                ticks="",
                gridcolor="rgba(255, 255, 255, 0.1)"
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc")
    )
    
    return fig