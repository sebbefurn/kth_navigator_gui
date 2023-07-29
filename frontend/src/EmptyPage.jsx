import { useState, useEffect, useRef } from 'react';
import './App.css';
import Papa from 'papaparse'
import axios from 'axios';

const EmptyPage = () => {
  
    return (
    <section className="Welcome">
        <div className="empty_container">
            <h1>KTH Navigator</h1>
            <div className="large-avatar"></div>
            <h3>Jag kan hjälpa dig att navigera campus och tolka ditt schema</h3>
        </div>
    </section>
    );
};

export default EmptyPage;