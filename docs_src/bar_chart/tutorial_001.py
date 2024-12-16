import plotly.graph_objects as go

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

primary_data = [20, 14, 25, 16, 18, 22, 19, 15, 12, 16, 14, 17]
secondary_data = [19, 14, 22, 14, 16, 19, 15, 14, 10, 12, 12, 16]

fig = go.Figure()
fig.add_trace(
    go.Bar(x=months, y=primary_data, name="Primary Product", marker_color="indianred")
)
fig.add_trace(
    go.Bar(
        x=months, y=secondary_data, name="Secondary Product", marker_color="lightsalmon"
    )
)

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(barmode="group", xaxis_tickangle=-45)
# fig.show()
