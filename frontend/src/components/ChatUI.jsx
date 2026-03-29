import React, { useState, useEffect } from 'react';

const ChatUI = () => {
    const [subject, setSubject] = useState('');
    const [examType, setExamType] = useState('');
    const [dataSaver, setDataSaver] = useState(false);
    const [messages, setMessages] = useState([]);

    const handleSubjectChange = (event) => {
        setSubject(event.target.value);
    };

    const handleExamTypeChange = (event) => {
        setExamType(event.target.value);
    };

    const toggleDataSaver = () => {
        setDataSaver(!dataSaver);
    };

    // Sample SSE listener for real-time data
    useEffect(() => {
        const eventSource = new EventSource('your-sse-endpoint');

        eventSource.onmessage = (event) => {
            setMessages((prevMessages) => [...prevMessages, JSON.parse(event.data)]);
        };

        return () => {
            eventSource.close();
        };
    }, []);

    return (
        <div style={{ padding: '10px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Chat Interface</h1>
            <div>
                <label>Select Subject:</label>
                <select value={subject} onChange={handleSubjectChange}>
                    <option value="">--Select Subject--</option>
                    <option value="Math">Math</option>
                    <option value="Science">Science</option>
                    <option value="History">History</option>
                </select>
            </div>
            <div>
                <label>Select Exam Type:</label>
                <select value={examType} onChange={handleExamTypeChange}>
                    <option value="">--Select Exam Type--</option>
                    <option value="Midterm">Midterm</option>
                    <option value="Final">Final</option>
                    <option value="Quiz">Quiz</option>
                </select>
            </div>
            <div>
                <label>
                    <input type="checkbox" onChange={toggleDataSaver} checked={dataSaver} /> Data Saver
                </label>
            </div>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                <h2>Messages:</h2>
                {messages.map((msg, index) => (
                    <div key={index}>{msg.text}</div>
                ))}
            </div>
        </div>
    );
};

export default ChatUI;