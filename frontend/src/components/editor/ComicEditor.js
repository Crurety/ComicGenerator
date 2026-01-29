import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { 
  fetchProjectComics,
  updateComicImage,
  selectLayers,
  selectSelectedLayer,
  selectCurrentTool,
  setSelectedLayer,
  setCurrentTool,
  updateLayer
} from '../../store/slices/editorSlice';
import ToolBar from './ToolBar';
import LayerPanel from './LayerPanel';
import CharacterPanel from './CharacterPanel';
import ScriptPanel from './ScriptPanel';

const ComicEditor = () => {
  const { projectId } = useParams();
  const dispatch = useDispatch();
  const layers = useSelector(selectLayers);
  const selectedLayer = useSelector(selectSelectedLayer);
  const currentTool = useSelector(selectCurrentTool);
  const canvasRef = useRef(null);

  // 侧边栏状态：'layers', 'characters', 'script'
  const [activePanel, setActivePanel] = useState('layers');

  // 拖拽状态
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0, layerId: null, initialLeft: 0, initialTop: 0 });

  useEffect(() => {
    if (projectId) {
      dispatch(fetchProjectComics(projectId));
    }
  }, [dispatch, projectId]);

  const handleLayerSelect = (layer, e) => {
    if (e) e.stopPropagation();
    dispatch(setSelectedLayer(layer));
  };

  const handleToolChange = (tool) => {
    dispatch(setCurrentTool(tool));
  };

  // 鼠标按下：开始拖拽
  const handleMouseDown = (e, layer) => {
    if (currentTool !== 'select') return;
    
    e.stopPropagation();
    handleLayerSelect(layer);
    
    setIsDragging(true);
    setDragStart({
      x: e.clientX,
      y: e.clientY,
      layerId: layer.id,
      initialLeft: layer.position_x || 0,
      initialTop: layer.position_y || 0
    });
  };

  // 鼠标移动：更新位置
  const handleMouseMove = (e) => {
    if (!isDragging || !dragStart.layerId) return;

    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;
    
    const newX = dragStart.initialLeft + dx;
    const newY = dragStart.initialTop + dy;

    // 实时更新 Redux 状态以实现流畅拖拽 (不保存到后端)
    dispatch(updateLayer({
      id: dragStart.layerId,
      position_x: newX,
      position_y: newY
    }));
  };

  // 鼠标松开：保存位置
  const handleMouseUp = (e) => {
    if (!isDragging || !dragStart.layerId) return;

    // 拖拽结束，发送请求保存到后端
    const layer = layers.find(l => l.id === dragStart.layerId);
    if (layer) {
      dispatch(updateComicImage({
        id: layer.id,
        position_x: layer.position_x,
        position_y: layer.position_y
      }));
    }

    setIsDragging(false);
    setDragStart({ x: 0, y: 0, layerId: null, initialLeft: 0, initialTop: 0 });
  };

  return (
    <div 
      className="comic-editor" 
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <ToolBar 
        currentTool={currentTool} 
        onToolChange={handleToolChange} 
      />
      
      <div className="editor-main">
        {/* 左侧图层面板已移动到右侧Tab */}
        
        <div className="canvas-container">
          <div className="canvas" ref={canvasRef}>
            {/* 画布内容 */}
            {layers.map(layer => (
              <div
                key={layer.id}
                className={`layer ${selectedLayer?.id === layer.id ? 'selected' : ''}`}
                style={{
                  position: 'absolute',
                  left: `${layer.position_x}px`,
                  top: `${layer.position_y}px`,
                  width: `${layer.width}px`,
                  height: `${layer.height}px`,
                  zIndex: layer.layer_order || 0,
                  border: selectedLayer?.id === layer.id ? '2px solid #667eea' : '1px solid #ddd',
                  cursor: currentTool === 'select' ? 'move' : 'default',
                  userSelect: 'none' // 防止拖拽时选中文本
                }}
                onMouseDown={(e) => handleMouseDown(e, layer)}
              >
                {layer.image_url ? (
                  <img 
                    src={layer.image_url} 
                    alt={layer.prompt}
                    style={{ width: '100%', height: '100%', objectFit: 'cover', pointerEvents: 'none' }}
                    onError={(e) => {
                      e.target.onerror = null; 
                      e.target.src = `https://ui-avatars.com/api/?name=Error&background=f00&color=fff&size=512`;
                    }}
                  />
                ) : (
                  <div style={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: '#f5f5f5',
                    fontSize: '12px',
                    color: '#666'
                  }}>
                    {layer.prompt || '空白图层'}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        
        <div className="right-sidebar">
            <div className="sidebar-tabs">
                <button 
                    className={activePanel === 'layers' ? 'active' : ''} 
                    onClick={() => setActivePanel('layers')}
                >图层</button>
                <button 
                    className={activePanel === 'characters' ? 'active' : ''} 
                    onClick={() => setActivePanel('characters')}
                >角色</button>
                 <button 
                    className={activePanel === 'script' ? 'active' : ''} 
                    onClick={() => setActivePanel('script')}
                >AI编剧</button>
            </div>
            
            <div className="sidebar-content">
                {activePanel === 'layers' && <LayerPanel 
                    layers={layers}
                    selectedLayer={selectedLayer}
                    onLayerSelect={(layer) => handleLayerSelect(layer, null)}
                />}
                {activePanel === 'characters' && <CharacterPanel projectId={projectId} />}
                {activePanel === 'script' && <ScriptPanel projectId={projectId} />}
            </div>
        </div>
      </div>
      
      <style jsx>{`
        .editor-main {
            display: flex;
            height: calc(100vh - 50px);
        }
        .canvas-container {
            flex: 1;
            background: #e2e8f0;
            overflow: auto;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .right-sidebar {
            width: 320px;
            background: white;
            border-left: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
        }
        .sidebar-tabs {
            display: flex;
            border-bottom: 1px solid #e2e8f0;
        }
        .sidebar-tabs button {
            flex: 1;
            padding: 12px;
            border: none;
            background: #f7fafc;
            cursor: pointer;
            font-weight: 500;
            color: #718096;
        }
        .sidebar-tabs button.active {
            background: white;
            color: #4299e1;
            border-bottom: 2px solid #4299e1;
        }
        .sidebar-content {
            flex: 1;
            overflow: hidden;
        }
      `}</style>
    </div>
  );
};

export default ComicEditor;
