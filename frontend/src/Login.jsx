import { useState } from 'react';
import './App.css';

const Login = ( {onLogin} ) => {
    const [grade, setGrade] = useState("");
    const [program, setProgram] = useState("");

    const handleLogin = (e) => {
        e.preventDefault();  // Prevent the default form submission behavior
        if (grade !== "" && program !== "") {
            console.log(grade);
            console.log(program);
            onLogin(parseInt(grade), program);
        } else {
            alert("Ange både program och årskurs")
        }
    }
  
    return (
        <div className='chatbox'>
        <section className="login-section">
            <div className="login-container">
                <h1>KTH Navigator</h1>
                <div className="large-avatar"></div>
                <form className='loggin-form' onSubmit={handleLogin}>
                    <label className="loggin-label" htmlFor="grade">Årskurs</label>
                    <select 
                        value={grade}
                        onChange={(e) => setGrade(e.target.value)}
                        className="loggin-options"
                    >
                        <option value="None">None</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                    </select>

                    <label className="loggin-label" htmlFor="program">Program</label>
                    <select 
                        value={program}
                        onChange={(e) => setProgram(e.target.value)}
                        className="loggin-options"
                    >
                        <option value="None">None</option>
                        <option value="Teknisk Fysik">Teknisk Fysik</option>
                    </select>
                    <button className="loggin-button" type="submit">Start</button>
                </form>
            </div>
        </section>
        </div>
    );
};

export default Login;
