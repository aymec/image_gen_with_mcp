import json
import requests
import uuid
import os
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# Configuration for the image generation service
IMAGE_GEN_URL = "http://localhost:5000/generate"

# Create the MCP server
mcp = FastMCP("image_generator")

@mcp.tool()
def generate_image(prompt: str) -> Dict[str, Any]:
    """
    Generate an image based on a text prompt using Stable Diffusion.
    
    Args:
        prompt: Text description of the image to generate
        
    Returns:
        Dictionary containing the image in a format compatible with MCP tools
    
    Usage:
        generate_image("A futuristic cityscape at sunset")
    """
    try:
        # Validate input
        if not prompt or not isinstance(prompt, str):
            raise McpError(
                ErrorData(
                    INVALID_PARAMS,
                    "A text prompt is required for image generation"
                )
            )
        
        # Call the image generation service
        response = requests.post(
            IMAGE_GEN_URL,
            json={"prompt": prompt}
        )
        
        if response.status_code != 200:
            raise McpError(
                ErrorData(
                    INTERNAL_ERROR,
                    f"Image generation failed: {response.text}"
                )
            )
        
        # Parse the response which contains the filename, path, and image data
        result = response.json()
        
        # Return the image data in MCP-compatible format
        return {
            "type": "image",
            "format": result["content_type"].split("/")[1],  # Get format from content_type
            "url": result["image_url"],  # Direct URL to image
            "width": result.get("width"),
            "height": result.get("height"),
            "filename": result["filename"],
            "filepath": result["filepath"],
            "mime_type": result["content_type"],
            "prompt": prompt,  # Include the original prompt
            "alt_text": f"AI-generated image of: {prompt}"  # Helpful for accessibility
        }
        
    except requests.RequestException as e:
        raise McpError(
            ErrorData(
                INTERNAL_ERROR,
                f"Request error: {str(e)}"
            )
        )
    except Exception as e:
        raise McpError(
            ErrorData(
                INTERNAL_ERROR,
                f"Failed to generate image: {str(e)}"
            )
        )