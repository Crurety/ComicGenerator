import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  analyzeStory, 
  saveStoryboards, 
  generateAllImages, 
  fetchStoryboards,
  updateScene,
  setActiveStep,
  selectStoryScenes,
  selectStoryStatus
} from '../../store/slices/storySlice';
import { fetchProjectComics } from '../../store/slices/editorSlice';

const ScriptPanel = ({ projectId }) => {
  const dispatch = useDispatch();
  const scenes = useSelector(selectStoryScenes);
  const { analyzing, generating, activeStep } = useSelector(selectStoryStatus);
  const [storyInput, setStoryInput] = useState('');

  // 加载已有分镜
  useEffect(() => {
    if (projectId) {
      dispatch(fetchStoryboards(projectId));
    }
  }, [dispatch, projectId]);

  const handleAnalyze = async () => {
    if (!storyInput.trim()) return;
    await dispatch(analyzeStory(storyInput));
  };

  const handleSave = async () => {
    await dispatch(saveStoryboards({ projectId, scenes }));
    alert('分镜脚本已保存');
  };

  const handleGenerate = async () => {
    // 先保存再生成
    await dispatch(saveStoryboards({ projectId, scenes }));
    await dispatch(generateAllImages(projectId));
    
    // 刷新画布图层
    dispatch(fetchProjectComics(projectId));
    // 重新拉取分镜以获取图片URL
    dispatch(fetchStoryboards(projectId));
    
    alert('所有图片生成任务已提交');
  };

  const renderStep1_Input = () => (
    <div className="step-content">
      <h3>1. 故事描述</h3>
      <p className="hint">输入你的故事大纲、场景描述或剧本草稿...</p>
      <textarea
        value={storyInput}
        onChange={(e) => setStoryInput(e.target.value)}
        placeholder="例如：在一个风雨交加的夜晚，侦探走进了古老的庄园..."
        rows={10}
        style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
      />
      <button 
        className="primary-btn" 
        onClick={handleAnalyze} 
        disabled={analyzing}
      >
        {analyzing ? 'AI 分析中...' : '生成分镜脚本'}
      </button>
    </div>
  );

  const renderStep2_Edit = () => (
    <div className="step-content">
      <div className="header-row">
        <h3>2. 分镜脚本确认</h3>
        <button onClick={handleSave} className="secondary-btn">保存进度</button>
      </div>
      <div className="scenes-list">
        {scenes.map((scene, index) => (
          <div key={index} className="scene-card">
            <div className="scene-header">
              <span className="scene-seq">场景 {scene.sequence}</span>
              <span className="scene-camera">{scene.camera}</span>
            </div>
            <div className="form-group">
              <label>画面描述:</label>
              <textarea
                value={scene.description}
                onChange={(e) => dispatch(updateScene({ index, field: 'description', value: e.target.value }))}
              />
            </div>
            <div className="form-group">
              <label>对话/旁白:</label>
              <input
                type="text"
                value={scene.dialogue || ''}
                onChange={(e) => dispatch(updateScene({ index, field: 'dialogue', value: e.target.value }))}
              />
            </div>
             <div className="form-group">
              <label>氛围:</label>
              <input
                type="text"
                value={scene.mood || ''}
                onChange={(e) => dispatch(updateScene({ index, field: 'mood', value: e.target.value }))}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="actions">
        <button onClick={() => dispatch(setActiveStep(0))} className="secondary-btn">返回修改故事</button>
        <button 
          className="primary-btn" 
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? '批量生成中...' : '生成所有漫画图片'}
        </button>
      </div>
    </div>
  );

  const renderStep3_Result = () => (
    <div className="step-content">
      <h3>3. 生成结果</h3>
      <div className="scenes-list">
        {scenes.map((scene, index) => (
          <div key={index} className="scene-card result-card">
             <div className="scene-header">
              <span className="scene-seq">场景 {scene.sequence}</span>
            </div>
            <div className="result-preview">
              {scene.image_url ? (
                 <img src={scene.image_url} alt={`Scene ${scene.sequence}`} />
              ) : (
                 <div className="placeholder">等待生成...</div>
              )}
            </div>
            <p className="scene-text">{scene.description}</p>
          </div>
        ))}
      </div>
      <div className="actions">
        <button onClick={() => dispatch(setActiveStep(1))} className="secondary-btn">返回编辑分镜</button>
        <button onClick={() => {
            dispatch(fetchProjectComics(projectId));
            alert('已同步到画布');
        }} className="primary-btn">同步到编辑器画布</button>
      </div>
    </div>
  );

  return (
    <div className="script-panel">
      <div className="panel-tabs">
        <button className={activeStep === 0 ? 'active' : ''} onClick={() => dispatch(setActiveStep(0))}>故事</button>
        <button className={activeStep === 1 ? 'active' : ''} onClick={() => dispatch(setActiveStep(1))}>分镜</button>
        <button className={activeStep === 2 ? 'active' : ''} onClick={() => dispatch(setActiveStep(2))}>结果</button>
      </div>
      
      <div className="panel-body">
        {activeStep === 0 && renderStep1_Input()}
        {activeStep === 1 && renderStep2_Edit()}
        {activeStep === 2 && renderStep3_Result()}
      </div>

      <style jsx>{`
        .script-panel {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: #fff;
          border-left: 1px solid #e2e8f0;
        }
        .panel-tabs {
          display: flex;
          border-bottom: 1px solid #e2e8f0;
        }
        .panel-tabs button {
          flex: 1;
          padding: 10px;
          background: none;
          border: none;
          cursor: pointer;
          font-weight: 500;
          color: #718096;
        }
        .panel-tabs button.active {
          color: #4299e1;
          border-bottom: 2px solid #4299e1;
        }
        .panel-body {
          flex: 1;
          overflow-y: auto;
          padding: 15px;
        }
        .step-content h3 {
          margin-top: 0;
          margin-bottom: 10px;
          font-size: 16px;
        }
        .hint {
          color: #718096;
          font-size: 12px;
          margin-bottom: 10px;
        }
        .primary-btn {
          width: 100%;
          padding: 10px;
          background: #4299e1;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 10px;
        }
        .primary-btn:disabled {
          background: #a0aec0;
        }
        .secondary-btn {
          padding: 5px 10px;
          background: #edf2f7;
          color: #4a5568;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        .scene-card {
          background: #f7fafc;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          padding: 10px;
          margin-bottom: 10px;
        }
        .scene-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-weight: bold;
          font-size: 13px;
        }
        .scene-camera {
          color: #ed8936;
          font-size: 12px;
        }
        .form-group {
          margin-bottom: 8px;
        }
        .form-group label {
          display: block;
          font-size: 12px;
          color: #718096;
          margin-bottom: 2px;
        }
        .form-group textarea, .form-group input {
          width: 100%;
          padding: 6px;
          border: 1px solid #cbd5e0;
          border-radius: 4px;
          font-size: 12px;
        }
        .header-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }
        .actions {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }
        .result-preview img {
          width: 100%;
          border-radius: 4px;
          margin-bottom: 5px;
        }
        .placeholder {
          width: 100%;
          height: 150px;
          background: #e2e8f0;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #a0aec0;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default ScriptPanel;
