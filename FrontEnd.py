import pandas as pd

from __init__ import threePackerProcess
import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import base64
import time
import random
from biSolver import biPackerProcess
import os

# Function to generate a random color
def generate_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Store(id='upload-state', data=False),  # Store to keep track of upload state
    dcc.Store(id='color-map', data={}),  # Store to keep track of color mapping
    dcc.Store(id='result-data', data=[]),  # Store to keep the result data
    dcc.Store(id='manual-items', data=[]),  # Store to keep manually entered items
    dcc.Store(id='combined-items', data=[]),  # Store to keep the combined items state

    html.Div([
        html.Div([
            html.H2("CONTAINER",
                    style={'backgroundColor': '#1B4F72', 'color': 'white', 'padding': '10px', 'margin': '0',
                           'textAlign': 'center', 'fontWeight': 'bold'}),
            html.Div([
                html.Div([
                    html.Div("Type", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                    dcc.Input(id='bin-type', value='Pallet', type='text', style={'width': '100%', 'marginBottom': '10px'})
                ], style={'flex': 1, 'padding': '5px'}),
                html.Div([
                    html.Div("Width = X Axis", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                    dcc.Input(id='bin-width', value='100', type='number', style={'width': '100%', 'marginBottom': '10px'})
                ], style={'flex': 1, 'padding': '5px'}),
                html.Div([
                    html.Div("Height = Y Axis", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                    dcc.Input(id='bin-height', value='100', type='number', style={'width': '100%', 'marginBottom': '10px'})
                ], style={'flex': 1, 'padding': '5px'}),
                html.Div([
                    html.Div("Depth = Z Axis", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                    dcc.Input(id='bin-depth', value='100', type='number', style={'width': '100%', 'marginBottom': '10px'})
                ], style={'flex': 1, 'padding': '5px'}),
                html.Div([
                    html.Div("Maximum Weight", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                    dcc.Input(id='bin-maxweight', value='15000', type='number', style={'width': '100%', 'marginBottom': '10px'})
                ], style={'flex': 1, 'padding': '5px'}),
            ], style={'display': 'flex', 'flexDirection': 'row', 'padding': '10px', 'border': '1px solid #1B4F72', 'borderRadius': '5px'}),
            html.Button("Show Result", id="start-packing-button", style={'width': '100%', 'marginBottom': '10px'})
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top', 'box-sizing': 'border-box', 'padding': '0px', 'margin': '0px'}),

        html.Div([
            html.H2("SOLVER SELECTION",
                    style={'backgroundColor': '#1B4F72', 'color': 'white', 'padding': '10px', 'margin': '0',
                           'textAlign': 'center', 'fontWeight': 'bold'}),
            html.Div([
                dcc.Dropdown(
                    id='solver-dropdown',
                    options=[
                        {'label': '2D Bin Packing Solver', 'value': '2DSolver'},
                        {'label': '3D Bin Packing Solver', 'value': '3DSolver'}
                    ],
                    value='3DSolver',
                    clearable=False,
                    style={'width': '200px', 'display': 'inline-block', 'margin-left': '10px'}
                ),
                dcc.Dropdown(
                    id='box-id-dropdown',
                    options=[],
                    placeholder='Select a box ID',
                    style={'width': '200px', 'display': 'inline-block', 'margin-left': '10px'}
                )
            ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'margin-top': '10px'})
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top', 'box-sizing': 'border-box', 'padding': '0px', 'margin': '0px'}),
    ], style={'display': 'flex', 'justify-content': 'flex-start', 'margin': '0px', 'padding': '0px'}),

    html.Div([
        html.H2("UPLOAD CSV", style={'backgroundColor': '#1B4F72', 'color': 'white', 'padding': '10px', 'margin': '0',
                                     'textAlign': 'center', 'fontWeight': 'bold'}),
        html.Div(id='upload-container', children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            html.Div(id='upload-status', style={'marginTop': '10px'}),
            html.Div(id='file-content', style={'marginTop': '10px'})  # New Div for file content
        ])
    ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top', 'box-sizing': 'border-box',
              'margin-top': '10px'}),
    html.Div([
        html.H2("MANUAL ITEM ENTRY",
                style={'backgroundColor': '#1B4F72', 'color': 'white', 'padding': '10px', 'margin': '0',
                       'textAlign': 'center', 'fontWeight': 'bold'}),
        html.Div([
            html.Div([
                html.Div("Part No (Unique)", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-partno', value='', type='text', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Name", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-name', value='', type='text', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Type (Only 'cube')", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Dropdown(id='item-type', options=[{'label': 'Cube', 'value': 'cube'}], value='cube', disabled=True,
                             style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Width", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-width', value='0', type='number', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Height", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-height', value='0', type='number', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Depth", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-depth', value='0', type='number', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Weight", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-weight', value='0', type='number', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Level (1, 2, or 3)", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Dropdown(id='item-level', options=[
                    {'label': '1', 'value': 1},
                    {'label': '2', 'value': 2},
                    {'label': '3', 'value': 3}
                ], value=1, style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Loadbear", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-loadbear', value='0', type='number', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Updown", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Dropdown(id='item-updown', options=[
                    {'label': 'True', 'value': 'true'},
                    {'label': 'False', 'value': 'false'}
                ], value='true', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Color (Optional)", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='item-color', value='', type='text', placeholder="#FFFFFF",
                          style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Div([
                html.Div("Rotation Allowed", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Dropdown(id='item-rotation', options=[
                    {'label': 'True', 'value': 'true'},
                    {'label': 'False', 'value': 'false'}
                ], value='true', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'})
        ], style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap', 'padding': '10px',
                  'border': '1px solid #1B4F72', 'borderRadius': '5px'}),
        html.Div([
            html.Button("Add Item", id="add-item-button", style={'width': '49%', 'marginRight': '1%'}),
            html.Button("Modify Item", id="modify-item-button", style={'width': '49%'})
        ], style={'marginTop': 20})
    ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top', 'box-sizing': 'border-box',
              'margin-top': '10px'}),

    html.Div([
        html.H2("DELETE ITEM", style={'backgroundColor': '#1B4F72', 'color': 'white', 'padding': '10px', 'margin': '0',
                                      'textAlign': 'center', 'fontWeight': 'bold'}),
        html.Div([
            html.Div([
                html.Div("Enter Part No to Delete", style={'marginBottom': '5px', 'font-family': 'Times New Roman'}),
                dcc.Input(id='delete-partno', value='', type='text', style={'width': '100%', 'marginBottom': '10px'})
            ], style={'flex': 1, 'padding': '5px'}),
            html.Button("Delete Item", id="delete-item-button", style={'width': '100%', 'marginBottom': '10px'})
        ], style={'display': 'flex', 'flexDirection': 'column', 'padding': '10px', 'border': '1px solid #1B4F72',
                  'borderRadius': '5px'})
    ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top', 'box-sizing': 'border-box',
              'margin-top': '10px'}),

    html.Div("VISUALIZATION",
             style={'backgroundColor': '#1B4F72', 'color': 'white', 'padding': '10px', 'textAlign': 'center'}),
    dcc.Graph(id='3d-scatter-plot'),

    html.Div([
        html.H2("METRICS", style={'backgroundColor': '#1B4F72', 'color': 'white', 'padding': '10px', 'margin': '0',
                                  'textAlign': 'center', 'fontWeight': 'bold'}),
        html.Div(id='metrics', style={'padding': '10px', 'border': '1px solid #1B4F72', 'borderRadius': '5px'})
    ], style={'marginTop': 20}),
    html.Div([
        html.Button("Download Fitted Results", id="download-fitted-button", style={'marginRight': '10px'}),
        dcc.Download(id="download-fitted"),
        html.Button("Download Unfitted Results", id="download-unfitted-button", style={'marginRight': '10px'}),
        dcc.Download(id="download-unfitted"),
        html.Button("Download Combined Results", id="download-combined-button", style={'marginRight': '10px'}),
        dcc.Download(id="download-combined"),
    ], style={'marginTop': 20, 'textAlign': 'center'}),
])

def find_item_name_by_partno(delete_partno, item_store):
    for item in item_store:
        if item["partno"] == delete_partno:
            return item["name"]

@app.callback(
    Output('box-id-dropdown', 'options'),
    Output('result-data', 'data'),
    Output('upload-status', 'children'),
    Output('upload-state', 'data'),
    Output('color-map', 'data'),
    Output('manual-items', 'data'),
    Output('file-content', 'children'),  # New Output for file content
    Output('combined-items', 'data'),  # Output for combined items state
    Input('upload-data', 'contents'),
    Input('add-item-button', 'n_clicks'),
    Input('delete-item-button', 'n_clicks'),
    Input('modify-item-button', 'n_clicks'),
    State('upload-data', 'filename'),
    State('color-map', 'data'),
    State('upload-state', 'data'),
    State('solver-dropdown', 'value'),
    State('item-partno', 'value'),
    State('item-name', 'value'),
    State('item-type', 'value'),
    State('item-width', 'value'),
    State('item-height', 'value'),
    State('item-depth', 'value'),
    State('item-weight', 'value'),
    State('item-level', 'value'),
    State('item-loadbear', 'value'),
    State('item-updown', 'value'),
    State('item-color', 'value'),
    State('item-rotation', 'value'),
    State('manual-items', 'data'),
    State('delete-partno', 'value'),
    State('combined-items', 'data')
)
def handle_inputs(contents, add_n_clicks, delete_n_clicks, modify_n_clicks, filename, color_map, upload_state, selected_solver,
                  partno, name, item_type, width, height, depth, weight, level,
                  loadbear, updown, color, rotation, manual_items, delete_partno, combined_items_state):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    box_id_options = []
    result_data = []
    upload_status = None
    color_map_return = color_map or {}
    manual_items_return = manual_items if manual_items is not None else []
    file_content = None  # To store the file content for display
    combined_items = combined_items_state if combined_items_state is not None else []

    # Initialize bin dimensions with default values
    bin_width = 100
    bin_height = 100
    bin_depth = 100

    if triggered_id == 'upload-data' and contents and filename:
        # Handle the file upload
        upload_status = 'Uploading...'
        time.sleep(1)

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        with open(filename, 'w') as f:
            f.write(decoded.decode('utf-8'))

        upload_status = f'Uploaded {filename} successfully'
        upload_state = True

        # Read uploaded file items
        combined_items = []
        if filename and os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_items = f.readlines()
                for item in existing_items[1:]:  # Skip header
                    part = item.strip().split(',')
                    combined_items.append({
                        'partno': part[0], 'name': part[1], 'type': part[2],
                        'width': int(part[3]), 'height': int(part[4]), 'depth': int(part[5]),
                        'weight': int(part[6]), 'level': int(part[7]), 'loadbear': int(part[8]),
                        'updown': part[9] == 'true', 'color': part[10], 'rotation_allowed': part[11] == 'true'
                    })

    if triggered_id == 'add-item-button' and add_n_clicks:
        # Handle the manual item addition
        if partno and name and all(item['partno'] != partno for item in combined_items + manual_items_return):
            new_item = {
                'partno': partno,
                'name': name,
                'type': item_type,
                'width': width,
                'height': height,
                'depth': depth,
                'weight': weight,
                'level': level,
                'loadbear': loadbear,
                'updown': updown == 'true',
                'color': color if color else generate_color(),
                'rotation_allowed': rotation == 'true'
            }

            # Add the new item to the manual items list
            manual_items_return.append(new_item)
            # Also add to the combined items list to keep state
            combined_items.append(new_item)
            # Update the color map with a unique color for the new item if not already present
            if name not in color_map_return:
                color_map_return[name] = new_item['color']

    if triggered_id == 'modify-item-button' and modify_n_clicks:
        # Handle the manual item modification
        for i, item in enumerate(combined_items):
            if item['partno'] == partno:
                combined_items[i] = {
                    'partno': partno,
                    'name': name,
                    'type': item_type,
                    'width': width,
                    'height': height,
                    'depth': depth,
                    'weight': weight,
                    'level': level,
                    'loadbear': loadbear,
                    'updown': updown == 'true',
                    'color': color if color else generate_color(),
                    'rotation_allowed': rotation == 'true'
                }
                break

        for i, item in enumerate(manual_items_return):
            if item['partno'] == partno:
                manual_items_return[i] = {
                    'partno': partno,
                    'name': name,
                    'type': item_type,
                    'width': width,
                    'height': height,
                    'depth': depth,
                    'weight': weight,
                    'level': level,
                    'loadbear': loadbear,
                    'updown': updown == 'true',
                    'color': color if color else generate_color(),
                    'rotation_allowed': rotation == 'true'
                }
                break

    # Handle item deletion
    if triggered_id == 'delete-item-button' and delete_n_clicks and delete_partno:
        # Remove from uploaded file items and manual items
        deleted_name = find_item_name_by_partno(delete_partno, combined_items)
        combined_items = [item for item in combined_items if item['partno'] != delete_partno]

        manual_items_return = [item for item in manual_items_return if item['partno'] != delete_partno]

        flag_com = True
        for item in combined_items:
            if item['name'] == deleted_name:
                flag_com = False
                break

        # Remove the corresponding color map entry
        if deleted_name in color_map_return and flag_com:
            del color_map_return[deleted_name]

    if combined_items:
        # Save combined items back to file
        temp_filename = 'temp_combined_items.csv'
        with open(temp_filename, 'w') as f:
            f.write("partno,name,type,width,height,depth,weight,level,loadbear,updown,color,rotation_allowed\n")
            for item in combined_items:
                f.write(f"{item['partno']},{item['name']},{item['type']},{item['width']},{item['height']},"
                        f"{item['depth']},{item['weight']},{item['level']},{item['loadbear']},"
                        f"{item['updown']},{item['color']},{item['rotation_allowed']}\n")

        # Process the combined data for packing
        if selected_solver == '3DSolver':
            status, fit_arr, raw_file_arr = threePackerProcess(bin_width, bin_height, bin_depth, temp_filename)
        else:
            status, fit_arr, raw_file_arr = biPackerProcess(bin_width, bin_height, bin_depth, temp_filename)
            if status == "error":
                status, fit_arr, raw_file_arr = threePackerProcess(bin_width, bin_height, bin_depth, temp_filename)

        # Update color map and result data
        for row in fit_arr:
            if row[0] not in color_map_return:
                color_map_return[row[0]] = generate_color()

        result_data = raw_file_arr

        # Cleanup temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    # Combine all items for display in file-content
    all_items_df = pd.DataFrame(combined_items)
    if not all_items_df.empty:
        file_content = html.Div([
            html.H4("Combined File and Manual Items"),
            dcc.Graph(
                figure={
                    'data': [
                        go.Table(
                            header=dict(values=list(all_items_df.columns)),
                            cells=dict(values=[all_items_df[col] for col in all_items_df.columns])
                        )
                    ],
                    'layout': go.Layout(title='Uploaded CSV and Manually Added Items')
                }
            )
        ])

    # Update box-id dropdown options
    if color_map_return:
        box_id_options = [{'label': 'Show All', 'value': 'ALL'}] + [{'label': key, 'value': key} for key in color_map_return.keys()]

    return box_id_options, result_data, upload_status, upload_state, color_map_return, manual_items_return, file_content, combined_items

@app.callback(
    Output('3d-scatter-plot', 'figure'),
    Output('metrics', 'children'),
    Input('solver-dropdown', 'value'),
    Input('start-packing-button', 'n_clicks'),
    Input('box-id-dropdown', 'value'),
    State('bin-width', 'value'),
    State('bin-depth', 'value'),
    State('bin-height', 'value'),
    State('result-data', 'data'),
    State('manual-items', 'data'),
    State('color-map', 'data'),
    State('upload-state', 'data'),
    State('upload-data', 'filename'))
def update_graph_and_metrics(selected_solver, start_packing_n_clicks, selected_box_id, bin_width, bin_depth, bin_height, result_arr, manual_items, color_map, upload_state, filename):
    # Initialize the figure and metrics
    fig = go.Figure()
    metrics = []
    error_message = None

    # Check the trigger context
    ctx = callback_context
    if not ctx.triggered or 'start-packing-button' not in ctx.triggered[0]['prop_id']:
        # If the Start Packing button was not clicked, return empty plot and metrics
        return fig, metrics

    # Proceed only if the Start Packing button was clicked
    bin_width = float(bin_width)
    bin_depth = float(bin_depth)
    bin_height = float(bin_height)

    fig.update_layout(
        scene=dict(
            aspectratio=dict(x=bin_width / bin_height, y=1, z=bin_depth / bin_height),
            xaxis=dict(nticks=10, range=[0, bin_width]),
            yaxis=dict(nticks=10, range=[0, bin_height]),
            zaxis=dict(nticks=10, range=[0, bin_depth])
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        title='3D Visualization',
        hovermode='closest'
    )

    # Combine result_data and manual_items for processing

    all_items = []
    if len(result_arr) == 0:
        all_items.extend(manual_items)
    else:
        all_items = result_arr

    # Ensure we have items to process
    if all_items:
        temp_filename = 'temp_combined_items.csv'
        with open(temp_filename, 'w') as f:
            f.write("partno,name,type,width,height,depth,weight,level,loadbear,updown,color,rotation_allowed\n")
            for item in all_items:
                if isinstance(item, dict):
                    f.write(f"{item.get('partno')},{item.get('name')},{item.get('type')},"
                            f"{item.get('width')},{item.get('height')},{item.get('depth')},"
                            f"{item.get('weight')},{item.get('level')},{item.get('loadbear')},"
                            f"{item.get('updown')},{item.get('color')},{item.get('rotation_allowed')}\n")
                else:
                    f.write(f"{item[0]},{item[1]},{item[2]},"
                            f"{item[3]},{item[4]},{item[5]},"
                            f"{item[6]},{item[7]},{item[8]},"
                            f"{item[9]},{item[10]},{item[11]}\n")

        # Process the file with the selected solver
        if selected_solver == '2DSolver':
            status, result, raw_file_arr = biPackerProcess(bin_width, bin_height, bin_depth, temp_filename)
        elif selected_solver == '3DSolver':
            status, result, raw_file_arr = threePackerProcess(bin_width, bin_height, bin_depth, temp_filename)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        if status == "error":
            error_message = result
            result_arr = []
        else:
            result_arr = result

    # Plot the boxes if there are any items in result_arr
    if result_arr:
        if selected_box_id and selected_box_id != 'ALL':
            result_arr = [row for row in result_arr if row[0] == selected_box_id]  # Filtering by name
        for row in result_arr:
            try:
                color = color_map.get(row[0], 'lightsalmon')
                fig.add_trace(
                    create_box(int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]),
                               int(row[6]), row[0], color)
                )
            except ValueError as e:
                print(f"Skipping item due to error: {e}. Item: {row}")
                continue

    total_volume = bin_width * bin_depth * bin_height
    used_volume = sum(int(row[4]) * int(row[5]) * int(row[6]) for row in result_arr)
    space_efficiency = (used_volume / total_volume) * 100 if total_volume > 0 else 0
    num_boxes = len(result_arr)

    metrics = [
        html.Div(f"Total Container Volume: {total_volume} cubic units"),
        html.Div(f"Used Volume: {used_volume} cubic units"),
        html.Div(f"Space Efficiency: {space_efficiency:.2f}%"),
        html.Div(f"Number of Boxes: {num_boxes}"),
        html.Div(f"Selected Solver: {selected_solver}")
    ]
    if error_message:
        metrics.append(html.Div(f"Error: {error_message}", style={'color': 'red'}))

    return fig, metrics



@app.callback(
    Output("download-fitted", "data"),
    Input("download-fitted-button", "n_clicks"),
    prevent_initial_call=True
)
def download_fitted_results(n_clicks):
    fitted_file_path = "fit.csv"
    return dcc.send_file(fitted_file_path)

@app.callback(
    Output("download-unfitted", "data"),
    Input("download-unfitted-button", "n_clicks"),
    prevent_initial_call=True
)
def download_unfitted_results(n_clicks):
    unfitted_file_path = "unfit.csv"
    return dcc.send_file(unfitted_file_path)

@app.callback(
    Output("download-combined", "data"),
    Input("download-combined-button", "n_clicks"),
    State('combined-items', 'data'),
    prevent_initial_call=True
)
def download_combined_results(n_clicks, combined_items):
    if combined_items:
        temp_filename = 'combined_items.csv'
        # Write the combined items to the CSV file
        with open(temp_filename, 'w') as f:
            f.write("partno,name,type,width,height,depth,weight,level,loadbear,updown,color,rotation_allowed\n")
            for item in combined_items:
                f.write(f"{item['partno']},{item['name']},{item['type']},{item['width']},{item['height']},"
                        f"{item['depth']},{item['weight']},{item['level']},{item['loadbear']},"
                        f"{item['updown']},{item['color']},{item['rotation_allowed']}\n")
        return dcc.send_file(temp_filename)
    return None
def create_box(x, y, z, width, height, depth, name, color):
    vertices = [
        (x, y, z),  # 0
        (x + width, y, z),  # 1
        (x + width, y + height, z),  # 2
        (x, y + height, z),  # 3
        (x, y, z + depth),  # 4
        (x + width, y, z + depth),  # 5
        (x + width, y + height, z + depth),  # 6
        (x, y + height, z + depth)  # 7
    ]

    i, j, k = zip(
        (0, 1, 2), (0, 2, 3),  # bottom face
        (4, 5, 6), (4, 6, 7),  # top face
        (0, 1, 5), (0, 5, 4),  # front face
        (2, 3, 7), (2, 7, 6),  # back face
        (1, 2, 6), (1, 6, 5),  # right face
        (0, 3, 7), (0, 7, 4)  # left face
    )

    return go.Mesh3d(
        x=[v[0] for v in vertices],
        y=[v[1] for v in vertices],
        z=[v[2] for v in vertices],
        i=i, j=j, k=k,
        name=name,
        color=color,
        opacity=0.8,
        hoverinfo='text',
        text=f'Box Type: {name}<br>Position: ({x}, {y}, {z})<br>Dimensions: ({width}, {height}, {depth})'
    )

if __name__ == '__main__':
    app.run_server(debug=True)
