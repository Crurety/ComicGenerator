import React from 'react';

const ToolBar = ({ currentTool, onToolChange }) => {
  const tools = [
    { id: 'select', name: '选择', icon: '↖' },
    { id: 'brush', name: '画笔', icon: '✏' },
    { id: 'text', name: '文本', icon: 'T' },
    { id: 'image', name: '图片', icon: '🖼' },
    { id: 'shape', name: '形状', icon: '⬜' }
  ];

  return (
    <div className="toolbar">
      {tools.map(tool => (
        <button
          key={tool.id}
          className={`tool-button ${currentTool === tool.id ? 'active' : ''}`}
          onClick={() => onToolChange(tool.id)}
          title={tool.name}
          data-tooltip={tool.name}
        >
          {tool.icon}
        </button>
      ))}
    </div>
  );
};

export default ToolBar;