import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { selectUser, logout } from '../../store/slices/authSlice';

const Layout = ({ children }) => {
  const user = useSelector(selectUser);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <div className="app">
      <header className="header">
        <h1>AI漫画编辑器</h1>
        <div className="user-info">
          <span>欢迎, {user?.username}</span>
          <button onClick={handleLogout}>退出</button>
        </div>
      </header>
      
      <div className="main-layout">
        <nav className="sidebar">
          <h3>导航</h3>
          <Link to="/dashboard" className="nav-item">仪表板</Link>
          <Link to="/characters" className="nav-item">角色管理</Link>
        </nav>
        
        <main className="content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;