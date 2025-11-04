import React, { useRef } from 'react';
import { ReactSketchCanvas } from 'react-sketch-canvas';

function DrawingCanvas({ onSave }) {
  const canvasRef = useRef(null);

  const handleSave = async () => {
    if (canvasRef.current) {
      const imageData = await canvasRef.current.exportImage('png');
      onSave({ imageData });
    }
  };

  const handleClear = () => {
    if (canvasRef.current) {
      canvasRef.current.clearCanvas();
    }
  };

  const handleUndo = () => {
    if (canvasRef.current) {
      canvasRef.current.undo();
    }
  };

  const handleRedo = () => {
    if (canvasRef.current) {
      canvasRef.current.redo();
    }
  };

  return (
    <div className="drawing-container">
      <div className="drawing-controls">
        <button type="button" onClick={handleUndo} className="drawing-btn">
          ↶ Undo
        </button>
        <button type="button" onClick={handleRedo} className="drawing-btn">
          ↷ Redo
        </button>
        <button type="button" onClick={handleClear} className="drawing-btn clear-btn">
          🗑️ Clear
        </button>
      </div>
      <ReactSketchCanvas
        ref={canvasRef}
        strokeWidth={3}
        strokeColor="#333"
        canvasColor="#ffffff"
        style={{
          border: '2px solid #e1e5e9',
          borderRadius: '12px',
        }}
        width="100%"
        height="400px"
      />
      <button type="button" onClick={handleSave} className="save-drawing-btn">
        ✓ Use This Drawing
      </button>
    </div>
  );
}

export default DrawingCanvas;
