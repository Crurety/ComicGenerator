import React, { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { 
  selectCharacters, 
  fetchCharacters 
} from '../../store/slices/characterSlice';
import { 
  generateImage, 
  checkGenerationStatus, 
  createComicImage,
  selectGenerating,
  selectGenerationResult,
  selectLayers
} from '../../store/slices/editorSlice';

const CharacterPanel = ({ projectId }) => {
  const dispatch = useDispatch();
  const characters = useSelector(selectCharacters);
  const layers = useSelector(selectLayers);
  const generating = useSelector(selectGenerating);
  const generationResult = useSelector(selectGenerationResult);
  
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [polling, setPolling] = useState(false);
  const generatingPromptRef = useRef('');

  useEffect(() => {
    dispatch(fetchCharacters());
  }, [dispatch]);

  // 监听生成结果并启动轮询
  useEffect(() => {
    if (generationResult?.task_id && !polling && !generating) {
       // 这里不直接启动，由handleGenerateImage控制流程更清晰，
       // 或者如果generationResult更新了，说明新任务开始了
    }
  }, [generationResult, generating]);

  // 轮询状态
  useEffect(() => {
    let intervalId;
    
    if (polling && generationResult?.task_id) {
      intervalId = setInterval(async () => {
        try {
          const result = await dispatch(checkGenerationStatus(generationResult.task_id)).unwrap();
          
          if (result.status === 'completed') {
            setPolling(false);
            // 计算最大图层顺序
            const maxOrder = layers.length > 0 
              ? Math.max(...layers.map(l => l.layer_order || 0)) 
              : 0;
              
            // 自动添加到画布
            dispatch(createComicImage({
              project_id: projectId,
              prompt: generatingPromptRef.current,
              image_url: result.image_url,
              midjourney_task_id: result.task_id,
              position_x: 0,
              position_y: 0,
              width: 512,
              height: 512,
              layer_order: maxOrder + 1
            }));
            alert('图片生成成功并已添加到画布！');
          } else if (result.status === 'failed') {
            setPolling(false);
            alert(`生成失败: ${result.error || '未知错误'}`);
          }
        } catch (error) {
          console.error("轮询状态出错:", error);
          // 不停止轮询，可能是临时网络错误
        }
      }, 2000);
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [polling, generationResult, dispatch, projectId]);

  const handleGenerateImage = async (characterId = null) => {
    if (!prompt.trim()) {
      alert('请输入描述文字');
      return;
    }

    try {
      generatingPromptRef.current = prompt;
      await dispatch(generateImage({
        project_id: projectId,
        prompt: prompt,
        character_template_id: characterId
      })).unwrap();
      
      setPolling(true);
    } catch (error) {
      console.error('生成图片失败:', error);
      alert('提交生成任务失败: ' + error);
    }
  };

  return (
    <div className="character-panel">
      <h3>角色与生成</h3>
      
      {/* 图片生成 */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h4>生成图片</h4>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="描述你想要生成的图片..."
          disabled={generating}
          style={{
            width: '100%',
            minHeight: '80px',
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '5px',
            marginBottom: '0.5rem'
          }}
        />
        <button
          onClick={() => handleGenerateImage()}
          disabled={generating || polling}
          style={{
            width: '100%',
            padding: '0.5rem',
            background: (generating || polling) ? '#ccc' : '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: (generating || polling) ? 'not-allowed' : 'pointer'
          }}
        >
          {(generating || polling) ? '生成中...' : '生成图片'}
        </button>
      </div>
      
      {/* 角色列表 */}
      <div>
        <h4>角色模板</h4>
        {characters.map(character => (
          <div
            key={character.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '5px',
              padding: '1rem',
              marginBottom: '0.5rem'
            }}
          >
            <h5>{character.name}</h5>
            <p style={{ fontSize: '0.8rem', color: '#666', margin: '0.5rem 0' }}>
              {character.description}
            </p>
            <button
              onClick={() => handleGenerateImage(character.id)}
              style={{
                width: '100%',
                padding: '0.25rem',
                background: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: 'pointer',
                fontSize: '0.8rem'
              }}
            >
              使用此角色
            </button>
          </div>
        ))}
        
        {characters.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '1rem',
            color: '#666',
            fontSize: '0.9rem'
          }}>
            <p>还没有角色模板</p>
            <small>前往角色管理创建角色</small>
          </div>
        )}
      </div>
      
      <button
        onClick={() => setShowCreateForm(true)}
        style={{
          width: '100%',
          padding: '0.5rem',
          background: '#ddd',
          color: '#333',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          marginTop: '1rem'
        }}
      >
        管理角色
      </button>
    </div>
  );
};

export default CharacterPanel;