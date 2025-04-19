import React, { useState, useRef } from 'react';
import './myStories.css';

/* ░░░ Central PDF‑upload box ░░░ */
const UploadBox = ({ stories }) => {
    const fileInputRef = useRef(null);
    const [chosenStory, setChosenStory] = useState('');
    const [fileName, setFileName] = useState('');
    const [status, setStatus] = useState('idle');   // idle | uploading | success | error
    const [apiResp, setApiResp] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    const API_ENDPOINT = 'http://localhost:5000/parse';   // your Flask/FastAPI endpoint

    const openPicker = () => fileInputRef.current?.click();

    /* immediately POST after a valid PDF is picked */
    const handleChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // ─── Validation ─────────────────────────────────────
        if (file.type !== 'application/pdf') {
            setErrorMsg('Please choose a PDF file');
            setStatus('error');
            console.error('Rejected: not a PDF');
            return;
        }
        if (!chosenStory) {
            setErrorMsg('Choose a story first');
            setStatus('error');
            console.error('Rejected: no story selected');
            return;
        }

        // ─── Build form‑data ───────────────────────────────
        setFileName(file.name);
        setStatus('uploading');
        setErrorMsg('');
        setApiResp(null);

        const fd = new FormData();
        fd.append('pdf', file);            // key MUST be “pdf”
        fd.append('storyName', chosenStory);

        // debug: log FormData entries
        for (const [k, v] of fd.entries()) {
            console.log('FormData ->', k, v);
        }

        // ─── POST ──────────────────────────────────────────
        try {
            console.log('Posting to', API_ENDPOINT);
            const resp = await fetch(API_ENDPOINT, { method: 'POST', body: fd });
            console.log('Response status', resp.status);

            if (!resp.ok) {
                const bodyText = await resp.text();
                console.error('Error body:', bodyText);
                throw new Error(`Server responded ${resp.status}`);
            }

            const json = await resp.json();
            console.log('Response JSON', json);
            setApiResp(json);
            setStatus('success');
        } catch (err) {
            console.error('Upload failed:', err);
            setErrorMsg(`Upload failed: ${err.message}`);
            setStatus('error');
        }
    };

    return (
        <div className="upload-box">
            <h3>Upload PDF to a Story</h3>

            <select
                className="story-dropdown"
                value={chosenStory}
                onChange={(e) => { setChosenStory(e.target.value); setStatus('idle'); }}
            >
                <option value="">Select Story</option>
                {stories.map((s, i) => (
                    <option key={i} value={s.name}>{s.name}</option>
                ))}
            </select>

            <button className="custom-upload-button" onClick={openPicker}>
                Choose PDF File
            </button>
            <input
                type="file"
                accept="application/pdf"
                style={{ display: 'none' }}
                ref={fileInputRef}
                onChange={handleChange}
            />

            {fileName && <div className="selected-file">Selected: {fileName}</div>}
            {status === 'uploading' && <div className="uploading-msg">Uploading…</div>}
            {status === 'success' && <div className="upload-success">Uploaded!</div>}
            {status === 'error' && <div className="upload-error">{errorMsg}</div>}

            {apiResp && (
                <div className="json-response-box">
                    <h4>API Response:</h4>
                    <pre>{JSON.stringify(apiResp, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

/* ░░░ Story grid ░░░ */
export const MyStories = ({ stories }) => {
    const [hover, setHover] = useState(null);

    return (
        <div className="my-stories-container">
            <h1>My Stories</h1>

            {stories.length === 0 ? (
                <div className="empty-stories">
                    <div className="empty-icon">📚</div>
                    <p>No stories yet. Start by creating one!</p>
                </div>
            ) : (
                <>
                    <div className="stories-grid">
                        {stories.map((s, i) => (
                            <div
                                key={i}
                                className={`story-folder ${hover === i ? 'hovered' : ''}`}
                                onMouseEnter={() => setHover(i)}
                                onMouseLeave={() => setHover(null)}
                            >
                                <div className="story-icon">📖</div>
                                <div className="story-name">{s.name}</div>
                                <div className="story-info">
                                    <span className="story-files">{s.files?.length || 0} files</span>
                                    <span className="story-date">Created today</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* global upload box */}
                    <UploadBox stories={stories} />
                </>
            )}
        </div>
    );
};
