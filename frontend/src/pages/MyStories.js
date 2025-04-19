import React, { useState } from 'react';
import './myStories.css';

export const MyStories = ({ stories }) => {
    const [hoveredStory, setHoveredStory] = useState(null);
    const [selectedStory, setSelectedStory] = useState(null);

    const handleStoryClick = (index) => {
        setSelectedStory(selectedStory === index ? null : index);
    };

    return (
        <div className="my-stories-container">
            <h1>My Stories</h1>

            {stories.length === 0 ? (
                <div className="empty-stories">
                    <div className="empty-icon">📚</div>
                    <p>No stories available yet.</p>
                    <p className="empty-hint">Create your first story to get started!</p>
                </div>
            ) : (
                <div className="stories-grid">
                    {stories.map((story, index) => (
                        <div
                            key={index}
                            className={`story-folder ${hoveredStory === index ? 'hovered' : ''} ${selectedStory === index ? 'selected' : ''}`}
                            onMouseEnter={() => setHoveredStory(index)}
                            onMouseLeave={() => setHoveredStory(null)}
                            onClick={() => handleStoryClick(index)}
                        >
                            <div className="story-icon">📖</div>
                            <div className="story-name">{story.name}</div>
                            <div className="story-info">
                                <span className="story-files">{story.files ? story.files.length : 0} files</span>
                                <span className="story-date">Created today</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
