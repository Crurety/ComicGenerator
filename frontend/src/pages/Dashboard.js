import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { 
  fetchProjects, 
  createProject, 
  selectProjects, 
  selectProjectLoading 
} from '../store/slices/projectSlice';

const Dashboard = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const projects = useSelector(selectProjects);
  const loading = useSelector(selectProjectLoading);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: ''
  });

  useEffect(() => {
    dispatch(fetchProjects());
  }, [dispatch]);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    
    try {
      await dispatch(createProject(newProject)).unwrap();
      setNewProject({ name: '', description: '' });
      setShowCreateForm(false);
    } catch (err) {
      console.error('创建项目失败:', err);
    }
  };

  const handleProjectClick = (projectId) => {
    navigate(`/editor/${projectId}`);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>我的项目</h2>
        <button 
          onClick={() => setShowCreateForm(true)}
          style={{
            padding: '0.75rem 1.5rem',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          新建项目
        </button>
      </div>

      {showCreateForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '10px',
            width: '100%',
            maxWidth: '500px'
          }}>
            <h3>创建新项目</h3>
            <form onSubmit={handleCreateProject}>
              <div style={{ marginBottom: '1rem' }}>
                <label>项目名称</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '5px'
                  }}
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label>项目描述</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    minHeight: '80px'
                  }}
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    padding: '0.5rem',
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px'
                  }}
                >
                  创建
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  style={{
                    flex: 1,
                    padding: '0.5rem',
                    background: '#ddd',
                    color: '#333',
                    border: 'none',
                    borderRadius: '5px'
                  }}
                >
                  取消
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading"></div>
      ) : (
        <div className="dashboard">
          {projects.map(project => (
            <div 
              key={project.id} 
              className="project-card"
              onClick={() => handleProjectClick(project.id)}
            >
              <h3>{project.name}</h3>
              <p>{project.description || '暂无描述'}</p>
              <div className="stats">
                <span>图片: {project.comic_images_count}</span>
                <span>协作者: {project.collaborators_count}</span>
              </div>
            </div>
          ))}
          
          {projects.length === 0 && (
            <div style={{
              textAlign: 'center',
              gridColumn: '1 / -1',
              padding: '3rem',
              color: '#666'
            }}>
              <p>还没有项目，点击上方"新建项目"按钮创建第一个项目吧！</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;