import React, { useState, useEffect } from 'react';

export const CreateStory = ({ setStories }) => {
    const [storyName, setStoryName] = useState('');
    const [showInput, setShowInput] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [inputError, setInputError] = useState('');

    // Handle creating a new story
    const handleAddStory = () => {
        setShowInput(true);
        setInputError('');
    };

    const handleStoryNameChange = (event) => {
        setStoryName(event.target.value);
        setInputError('');
    };

    const handleStorySubmit = () => {
        if (!storyName.trim()) {
            setInputError('Please enter a story name');
            return;
        }

        setIsSubmitting(true);

        // Simulate a brief loading state for better UX
        setTimeout(() => {
            // Create new story and add to the list of stories
            setStories((prevStories) => [
                ...prevStories,
                { name: storyName, files: [] }, // Add the new story here
            ]);

            setSuccessMessage(`Story "${storyName}" created successfully!`);
            setShowInput(false);
            setStoryName('');
            setIsSubmitting(false);

            // Clear success message after 3 seconds
            setTimeout(() => {
                setSuccessMessage('');
            }, 3000);
        }, 800);
    };

    // Handle Enter key press
    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleStorySubmit();
        }
    };

    return (
        <div className="create-story-container">
            <div className="create-story-header">
                <h1>Create a New Story</h1>
                <p>Start your creative journey by creating a new story. Give it a meaningful name and begin your adventure.</p>
            </div>

            <div className="create-story-content">
                {successMessage && (
                    <div className="success-message">
                        {successMessage}
                    </div>
                )}

                {!showInput ? (
                    <div className="create-story-form">
                        <p>Ready to create something amazing? Click the button below to get started.</p>
                        <div className="form-actions">
                            <button onClick={handleAddStory} className="story-button">
                                Create New Story
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="create-story-form">
                        <div className="form-group">
                            <label htmlFor="storyName">Story Name</label>
                            <input
                                id="storyName"
                                type="text"
                                value={storyName}
                                onChange={handleStoryNameChange}
                                onKeyPress={handleKeyPress}
                                placeholder="Enter a name for your story"
                                className={inputError ? 'input-error' : ''}
                                autoFocus
                            />
                            {inputError && <div className="error-message">{inputError}</div>}
                        </div>
                        <div className="form-actions">
                            <button
                                onClick={handleStorySubmit}
                                className={`story-button ${isSubmitting ? 'submitting' : ''}`}
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? 'Creating...' : 'Create Story'}
                            </button>
                            <button
                                onClick={() => setShowInput(false)}
                                className="story-button secondary"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
