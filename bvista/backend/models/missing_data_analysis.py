import matplotlib
matplotlib.use("Agg")  # ✅ Prevent GUI-related crashes in Flask

import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from bvista.backend.models.data_manager import get_session
from flask import jsonify
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)


def analyze_missing_pattern(session_id, selected_columns=None):
    """
    Generate a missing data pattern matrix and return it as a base64 image.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of columns to include in analysis.
    :return: JSON containing base64-encoded image of missing data visualization.
    """
    # ✅ Get dataset from session
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy(deep=True)  # Safe copy to avoid modifying original data

    # ✅ Handle column selection safely
    if selected_columns:
        missing_cols = [col for col in selected_columns if col not in df.columns]
        if missing_cols:
            return {"error": f"Columns not found: {missing_cols}"}
        df = df[selected_columns]

    # ✅ Dynamically scale figure size
    num_cols = df.shape[1]
    num_rows = df.shape[0]

    # ✅ Maintain consistent column width while allowing horizontal scrolling
    base_width_per_column = 0.7  # Each column gets a fixed width
    total_width = max(10, num_cols * base_width_per_column)  # Minimum width of 10 inches

    base_height = min(7, max(5, num_rows / 100))  # Scale height but prevent excessive stretching

    # ✅ Generate the missing data matrix using missingno
    fig, ax = plt.subplots(figsize=(total_width, base_height))
    msno.matrix(df, fontsize=12, ax=ax)  # Generate missing pattern plot

    # ✅ Truncate long column names (>20 characters)
    truncated_labels = [col[:20] + "..." if len(col) > 30 else col for col in df.columns]

    # ✅ Force column names to always remain visible
    rotation_angle = 90  
    ax.set_xticks(range(num_cols))  # Manually set x-ticks
    ax.set_xticklabels(truncated_labels, rotation=rotation_angle, fontsize=12, ha="right")  # Rotate and ensure visibility
    plt.subplots_adjust(bottom=0.3)  # Ensure space for column labels

    # ✅ Convert plot to base64 image
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)  # Close figure to free memory
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # ✅ Return JSON response with the base64 image
    return jsonify({
        "session_id": session_id,
        "image_base64": image_base64  # Send base64 string to frontend
    })






def analyze_missing_correlation(session_id, selected_columns=None):
    """
    Generate a missing data correlation heatmap and return it as a base64 image.
    """
    # ✅ Get dataset from session
    session = get_session(session_id)
    if session is None:
        logging.error("Session not found!")
        return jsonify({"error": "Session not found"})

    df = session["df"].copy(deep=True)  # Safe copy to avoid modifying original data

    # ✅ Handle column selection safely
    if selected_columns:
        missing_cols = [col for col in selected_columns if col not in df.columns]
        if missing_cols:
            logging.error(f"Columns not found: {missing_cols}")
            return jsonify({"error": f"Columns not found: {missing_cols}"})
        df = df[selected_columns]

    num_cols = df.shape[1]

    # ✅ Ensure minimum width per column and height per row
    min_cell_size = 0.5  # Minimum size per cell
    total_width = max(12, num_cols * min_cell_size)  # Ensure width scales properly
    total_height = max(8, num_cols * min_cell_size)  # Ensure height scales properly

    # ✅ Generate missing data correlation heatmap using missingno
    fig, ax = plt.subplots(figsize=(total_width, total_height))

    try:
        # ✅ Check if missing values exist
        if df.isnull().sum().sum() == 0:
            logging.warning("No missing data correlation detected.")
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_frame_on(False)
            plt.grid(False)
            plt.text(0.5, 0.5, "No Missing Data Correlation", 
                     horizontalalignment='center',  
                     verticalalignment='center', 

                     transform=ax.transAxes, fontsize=14, color="gray")
        else:
            logging.info(f"Generating missing correlation heatmap for {num_cols} columns...")
            msno.heatmap(df, ax=ax, fontsize=10, cmap="coolwarm")  # Standard heatmap

            # ✅ Get the actual column names used in the heatmap
            xticklabels = [label.get_text() for label in ax.get_xticklabels()]
            yticklabels = [label.get_text() for label in ax.get_yticklabels()]

            # ✅ Rotate x-axis labels properly
            ax.set_xticklabels(xticklabels, rotation=90, fontsize=10, ha="right")

        # ✅ Adjust spacing for better readability
        plt.subplots_adjust(left=0.3, top=0.95, right=0.95, bottom=0.3)

        # ✅ Convert plot to base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
        plt.close(fig)  # Free memory
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return jsonify({
            "session_id": session_id,
            "image_base64": image_base64  # Send base64 string to frontend
        })

    except Exception as e:
        logging.error(f"❌ Error generating missing correlation heatmap: {e}")
        return jsonify({"error": f"Missing data correlation failed: {str(e)}"})



















def analyze_missing_distribution(session_id, selected_columns=None):
    """
    Generate a missing data distribution bar chart and return it as a base64 image.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of columns to include in analysis.
    :return: JSON containing base64-encoded image of missing data distribution.
    """
    # ✅ Get dataset from session
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy(deep=True)  # Safe copy to avoid modifying original data

    # ✅ Handle column selection safely
    if selected_columns:
        missing_cols = [col for col in selected_columns if col not in df.columns]
        if missing_cols:
            return {"error": f"Columns not found: {missing_cols}"}
        df = df[selected_columns]

    # ✅ Dynamically scale figure size based on the number of columns
    num_cols = df.shape[1]
    num_rows = df.shape[0]

    base_width_per_column = 0.7  # Each column gets a fixed width
    total_width = max(10, num_cols * base_width_per_column)  # Minimum width of 10 inches

    # ✅ Default height when columns are small
    base_height = min(7, max(5, num_rows / 100))  

    # ✅ Check if Missingno is flipping the chart
    should_flip = num_cols > 50  # Flips when there are more than 50 columns

    if should_flip:
        base_height = max(10, num_cols * 0.5)  # Increase height for readability

    # ✅ Generate the missing data bar chart
    fig, ax = plt.subplots(figsize=(total_width, base_height))
    msno.bar(df, fontsize=12, ax=ax, color="blue")  # Generate missing distribution plot

    # ✅ Adjustments when the chart flips
    if should_flip:
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)  # Make Y-axis labels readable
        plt.subplots_adjust(left=0.3, right=0.95, top=0.95, bottom=0.05)  # Adjust margins


    else:
        # ✅ Force column names to always remain visible
        truncated_labels = [col[:20] + "..." if len(col) > 30 else col for col in df.columns]
        rotation_angle = 90  
        ax.set_xticks(range(num_cols))  # Manually set x-ticks
        ax.set_xticklabels(truncated_labels, rotation=rotation_angle, fontsize=10, ha="right")  
        plt.subplots_adjust(bottom=0.3)  # Ensure space for column labels

    # ✅ Convert plot to base64 image
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)  # Free memory
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # ✅ Return JSON response with the base64 image
    return jsonify({
        "session_id": session_id,
        "image_base64": image_base64  # Send base64 string to frontend
    })







def analyze_missing_hierarchical(session_id, selected_columns=None):
    """
    Perform hierarchical clustering of missing data and return a base64-encoded dendrogram image.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of columns to include in analysis.
    :return: JSON containing base64-encoded image of the missing data dendrogram.
    """
    # ✅ Get dataset from session
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"})

    df = session["df"].copy(deep=True)  # Safe copy to avoid modifying original data

    # ✅ Handle column selection safely
    if selected_columns:
        missing_cols = [col for col in selected_columns if col not in df.columns]
        if missing_cols:
            return jsonify({"error": f"Columns not found: {missing_cols}"})
        df = df[selected_columns]

    # ✅ Ensure missing values exist
    if df.isnull().sum().sum() == 0:
        logging.warning("No missing values detected for hierarchical clustering.")
        return jsonify({"error": "No missing data found to cluster."})

    # ✅ Determine if flipping occurs (when columns exceed 50)
    num_cols = df.shape[1]
    should_flip = num_cols > 50

    # ✅ Dynamically adjust figure size based on column count
    if should_flip:
        total_width = max(18, num_cols * 0.22)  # Adjust width for large datasets
        total_height = max(15, min(35, num_cols * 0.5))  # Ensure proper scaling
    else:
        total_width = max(10, num_cols * 0.5)  # Smaller datasets need less width
        total_height = max(7, num_cols * 0.3)  # Proper height scaling

    # ✅ Generate hierarchical clustering dendrogram
    fig, ax = plt.subplots(figsize=(total_width, total_height))
    msno.dendrogram(df, fontsize=12, ax=ax)  # Generate hierarchical clustering

    # ✅ Rotate column labels **always** for better readability
    for label in ax.get_xticklabels():
        label.set_rotation(90)
        label.set_fontsize(10)
        label.set_ha("right")

    # ✅ Improve spacing between bars and labels
    ax.xaxis.set_tick_params(pad=8)  # Adds space between labels and axis
    ax.yaxis.set_tick_params(pad=5)  # Adds space between y-axis ticks

    # ✅ Adjust layout to prevent overlap
    plt.subplots_adjust(left=0.3, right=0.95, top=0.95, bottom=0.4)  # Increase bottom margin

    # ✅ Convert plot to base64 image
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)  # Free memory
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # ✅ Return JSON response with the base64 image
    return jsonify({
        "session_id": session_id,
        "image_base64": image_base64  # Send base64 string to frontend
    })















