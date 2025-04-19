import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

export const Navbar = () => {
    const location = useLocation();
    const [activeItem, setActiveItem] = useState(location.pathname);

    const handleMouseEnter = (path) => {
        setActiveItem(path);
    };

    const handleMouseLeave = () => {
        setActiveItem(location.pathname);
    };

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <div className="logo-container">
                    <div className="logo-circle">
                        <span className="logo-text">SA</span>
                    </div>
                </div>
                <h2 className="sidebar-title" data-text="PlotHub">PlotHub</h2>
            </div>
            <ul className="sidebar-list">
                <li>
                    <Link
                        to="/home"
                        className={`sidebar-link ${location.pathname === '/home' || location.pathname === '/' ? 'active' : ''}`}
                        onMouseEnter={() => handleMouseEnter('/home')}
                        onMouseLeave={handleMouseLeave}
                    >
                        <i className="nav-icon home-icon"></i>
                        <span>Home</span>
                    </Link>
                </li>
                <li>
                    <Link
                        to="/mystories"
                        className={`sidebar-link ${location.pathname === '/mystories' ? 'active' : ''}`}
                        onMouseEnter={() => handleMouseEnter('/mystories')}
                        onMouseLeave={handleMouseLeave}
                    >
                        <i className="nav-icon stories-icon"></i>
                        <span>My Stories</span>
                    </Link>
                </li>
                <li>
                    <Link
                        to="/createstory"
                        className={`sidebar-link ${location.pathname === '/createstory' ? 'active' : ''}`}
                        onMouseEnter={() => handleMouseEnter('/createstory')}
                        onMouseLeave={handleMouseLeave}
                    >
                        <i className="nav-icon create-icon"></i>
                        <span>Create New Story</span>
                    </Link>
                </li>
                <li>
                    <Link
                        to="/settings"
                        className={`sidebar-link ${location.pathname === '/settings' ? 'active' : ''}`}
                        onMouseEnter={() => handleMouseEnter('/settings')}
                        onMouseLeave={handleMouseLeave}
                    >
                        <i className="nav-icon settings-icon"></i>
                        <span>Settings</span>
                    </Link>
                </li>
                <li className="logout-item">
                    <Link
                        to="/logout"
                        className={`sidebar-link ${location.pathname === '/logout' ? 'active' : ''}`}
                        onMouseEnter={() => handleMouseEnter('/logout')}
                        onMouseLeave={handleMouseLeave}
                    >
                        <i className="nav-icon logout-icon"></i>
                        <span>Logout</span>
                    </Link>
                </li>
            </ul>
        </div>
    );
};
