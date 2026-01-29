import React from 'react';
import { useDispatch } from 'react-redux';
import { deleteComicImage } from '../../store/slices/editorSlice';

const LayerPanel = ({ layers, selectedLayer, onLayerSelect }) => {
  const dispatch = useDispatch();

  const handleLayerClick = (layer) => {
    onLayerSelect(layer);
  };

  const handleDeleteLayer = (e, layerId) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个图层吗？')) {
      dispatch(deleteComicImage(layerId));
    }
  };

  const sortedLayers = [...layers].sort((a, b) => b.layer_order - a.layer_order);

  return (
    <div className="layer-panel">
      <h3>图层</h3>
      
      {sortedLayers.map(layer => (
        <div
          key={layer.id}
          className={`layer-item ${selectedLayer?.id === layer.id ? 'selected' : ''}`}
          onClick={() => handleLayerClick(layer)}
        >
          <div className="layer-info">
            <div>{layer.prompt || `图层 ${layer.id}`}</div>
            <small>{layer.status}</small>
          </div>
          
          <div className="layer-actions">
            <button 
              onClick={(e) => handleDeleteLayer(e, layer.id)}
              title="删除"
            >
              🗑
            </button>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                // TODO: 实现图层锁定
              }}
              title="锁定"
            >
              🔒
            </button>
          </div>
        </div>
      ))}
      
      {layers.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '2rem',
          color: '#666'
        }}>
          <p>还没有图层</p>
          <small>使用工具栏添加内容</small>
        </div>
      )}
    </div>
  );
};

export default LayerPanel;