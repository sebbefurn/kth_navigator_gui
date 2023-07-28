import { useState, useEffect, useRef } from 'react';
import './App.css';
import Papa from 'papaparse'
import axios from 'axios';

function App() {
  const [selectedValue, setSelectedValue] = useState(1) 
  const [user_id, setUserId] = useState()
  const [input, setInput] = useState("");
  const [chatLog, setChatLog] = useState([]);

  useEffect(() => {
  // Function to create a new user
  const createUser = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/create-user/', {
        course: null,
        grade: null,
      });
      const new_id = response.data['user_id']; // Get the user ID from the response
      setUserId(new_id);
      console.log(new_id);
    } catch (error) {
      console.error(error);
    }
  };

    createUser(); // Call the function to create a new user when the component mounts
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setChatLog((chatLog) => [...chatLog, {user: "me", message: `${input}`}]);
    setInput("");
    axios.post('http://localhost:8000/api/create-text/', {
      text: `${input}`,
      user: user_id,
      is_user: true,
      grade: selectedValue,
    })
      .then(response => {
        // Handle the response (e.g., display success message)
        const gpt_message = response.data['message'];
        console.log(gpt_message)
        setChatLog((chatLog) => [...chatLog, {user: "gpt", message: `${gpt_message}`}]);
        console.log(gpt_message);
      })
      .catch(error => {
        // Handle any errors
        console.error(error);
    });
  }

  const chatLogRef = useRef(null);

  // Function to scroll to the bottom of the chat log container
  const scrollToBottom = () => {
    chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
  };

  // Scroll to bottom whenever the chatLog updates
  useEffect(() => {
    scrollToBottom();
  }, [chatLog]);

  return (
  <div className="App">
    <section className="chatbox">
      <div className="chat-log" ref={chatLogRef}>
        {chatLog.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
      </div>
    <div className="chat-input-holder">
      <form onSubmit={handleSubmit}>
        <div className="input-container">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="chat-input-textarea"
            placeholder="Type here"
          />
        <p className='small_text'>Grade:</p>
          <select
            value={selectedValue}
            onChange={(e) => setSelectedValue(parseInt(e.target.value))}
            className="multiple-choice-box"
          >
            {[1, 2, 3, 4, 5].map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </form>
    </div>
    </section>
  </div>
  );
}

const ChatMessage = ({ message }) => {
  const convertToLinks = (inputString) => {
    const regex = /\[(\w+),\((https:\/\/www\.google\.com\/maps\/place\/[\d\.,]+)\),(\d+)\]/g;

    let tempText = inputString;
    let match;

    while ((match = regex.exec(inputString)) !== null) {
      const room = match[1];
      const url = match[2];
      const floor = match[3];
      
      const link = `<a href="${url}" target="_blank" rel="noopener noreferrer">${room}</a>`;
      tempText = tempText.replace(match[0], link);
    }

    return tempText;
  };

  const createTableRows = (inputString) => {
    const lines = inputString.split('\n');
    const tableRows = lines.filter(line => isTableRow(line));
    const nonTableRows = lines.filter(line => !isTableRow(line));

    const renderTable = tableRows.map((line, index) => {
      const row = Papa.parse(line, { delimiter: ',', skipEmptyLines: true }).data[0];

      const columns = row.map((cell, cellIndex) => {
        const convertedCell = convertToLinks(cell);
        return <td key={cellIndex} dangerouslySetInnerHTML={{ __html: convertedCell }}></td>;
      });

      return <tr key={index}>{columns}</tr>;
    });

    const renderNonTable = nonTableRows.map((line, index) => <p key={index}>{line}</p>);

    return (
      <div>
        <table><tbody>{renderTable}</tbody></table>
        {renderNonTable}
      </div>
    );
  };


  const isTableRow = (text) => {
    const dateRegex = /^\d{4}-\d{2}-\d{2},/;
    const second_regex = /^Startdatum,Starttid/
    return dateRegex.test(text) || second_regex.test(text);
  };
   
  return (
    <div className={`chat-message ${message.user === "gpt" && "chatgpt"}`}>
      <div className="chat-message-center">
        <div className={`avatar ${message.user === "gpt" && "chatgpt"}`}></div>
        <div className="message" style={{ whiteSpace: "pre-wrap" }}>
          {createTableRows(message.message)}
        </div>
      </div>
    </div>
  );
};


export default App;