import streamlit as st
from wall import Wall
from wall_builder import WallBuilder

# Initialize session state
if 'wall' not in st.session_state:
    st.session_state.wall = None
if 'wall_builder' not in st.session_state:
    st.session_state.wall_builder = None
if 'selected_wall_type' not in st.session_state:
    st.session_state.selected_wall_type = "Stretcher"  # Default bond type
if 'wall_width' not in st.session_state:
    st.session_state.wall_width = 2300
if 'wall_height' not in st.session_state:
    st.session_state.wall_height = 2000

# Sidebar configuration
def setup_sidebar():
    with st.sidebar:
        bond_types = ["Stretcher", "English", "Wild"]

        # Wall type selection with callback
        def on_wall_type_change():
            st.session_state.wall = Wall(
                width=st.session_state.wall_width, 
                height=st.session_state.wall_height, 
                type=st.session_state.selected_wall_type
            )
            st.session_state.wall_builder = WallBuilder(wall=st.session_state.wall)

        st.radio(
            "Choose Bond Type:",
            bond_types,
            key='selected_wall_type',
            on_change=on_wall_type_change,
        )
        
        # Calculate the frame position for display
        frame_x_end = min(st.session_state.wall_builder.frame_x + st.session_state.wall_builder.frame_width, st.session_state.wall.width)
        frame_y_end = min(st.session_state.wall_builder.frame_y + st.session_state.wall_builder.frame_height, st.session_state.wall.height)

        if st.session_state.wall:
            st.write(f"X position of frame: {st.session_state.wall_builder.frame_x} - {frame_x_end} mm")
            st.write(f"Y position of frame: {st.session_state.wall_builder.frame_y} - {frame_y_end} mm")
            st.write(f"Total Moves: {st.session_state.wall_builder.total_moves}")
        
        with st.expander('Experimental options'):
            st.write('These options are not guaranteed to work optimally in all settings!')

            st.session_state.wall_width = st.number_input('Set the width of the wall (default = 2300 mm)', 220,step=220, value=2300)
            st.session_state.wall_height = st.number_input('Set the width of the wall (default = 2000 mm)', 63, step=63, value=2000)
            st.button('Reset', on_click=on_wall_type_change)


# Main application
def main():
    st.title("Brick Wall Builder")

    # Initialize wall if not already initialized
    if st.session_state.wall is None:
        st.session_state.wall = Wall(
                width=st.session_state.wall_width, 
                height=st.session_state.wall_height, 
            type=st.session_state.selected_wall_type
        )  
    if st.session_state.wall_builder is None:
        st.session_state.wall_builder = WallBuilder(wall=st.session_state.wall)


    # Sidebar setup
    setup_sidebar()

    # Display build actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Lay Bricks Until Next Move'):
            success, message = st.session_state.wall_builder.execute_next_best_move()
            st.write(message)

    with col2:
        if st.button('Lay Next Brick'):
            success, message = st.session_state.wall_builder.execute_next_best_move(single=True)
            st.write(message)
    st.write("**Sequence of Build Strides:**")
    st.code("▓▓ -> ░░ -> @@ -> ██ -> ## -> $$ -> && -> ▒▒ -> ++ -> ==", language=None)

    # Wall visualization
    st.session_state.wall.visualize_wall()

    # Use container for consistent output accross browsers
    with st.container():
        st.code(st.session_state.wall.wall_visual, language=None)


if __name__ == "__main__":
    main()
