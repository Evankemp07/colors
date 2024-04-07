import numpy as np
import pytest
from mainGUI import average_color, generate_svg

@pytest.fixture
def tmp_svg_path(tmp_path):
    return tmp_path / "average_colors.svg"

def test_average_color():
    # Create a test image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :, 0] = 255  # Set blue channel to maximum

    # Test the average_color function
    avg_color = average_color(image)

    # Check if the average color is blue
    assert np.array_equal(avg_color, [0, 0, 255]), "Average color calculation is incorrect"

def test_generate_svg(tmp_svg_path):
    # Create some sample colors
    colors = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]

    # Generate SVG with sample colors
    generate_svg(colors, str(tmp_svg_path))

    # Check if SVG file is generated
    assert tmp_svg_path.exists(), "SVG file is not generated"

    # Check if SVG file has correct content
    with open(tmp_svg_path, "r") as f:
        svg_content = f.read()
        assert '<rect x="0.0" y="0" width="800.0" height="600" fill="rgb(255, 0, 0)"/>' in svg_content, "SVG content is incorrect"
        assert '<rect x="800.0" y="0" width="800.0" height="600" fill="rgb(0, 255, 0)"/>' in svg_content, "SVG content is incorrect"
        assert '<rect x="1600.0" y="0" width="800.0" height="600" fill="rgb(0, 0, 255)"/>' in svg_content, "SVG content is incorrect"
        
# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
