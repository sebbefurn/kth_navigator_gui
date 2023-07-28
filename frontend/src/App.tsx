import { useState, useEffect, useRef } from 'react';
import './App.css';
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
  // Function to detect if a string is a valid URL
  const isURL = (str) => {
    try {
      new URL(str);
      return true;
    } catch (err) {
      return false;
    }
  };

  // Function to convert URLs in the message to clickable links with room identifier and floor number
  const convertToLinks = (text) => {
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const messageWithLinks = [];
    let match;
    let lastIndex = 0;
  
    while ((match = linkRegex.exec(text)) !== null) {
      const linkText = match[1];
      const linkURL = match[2];
  
      // Add the text before the link as regular text
      if (match.index !== lastIndex) {
        const regularText = text.slice(lastIndex, match.index);
        messageWithLinks.push(regularText);
      }
  
      // Create the anchor tag for the link
      messageWithLinks.push(
        <a
          key={match.index}
          href={linkURL}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "#ffffff" }}
        >
          {linkText}
        </a>
      );
  
      lastIndex = linkRegex.lastIndex;
    }
  
    // Add any remaining text after the last link as regular text
    if (lastIndex < text.length) {
      const remainingText = text.slice(lastIndex);
      messageWithLinks.push(remainingText);
    }
  
    return messageWithLinks;
  };
   
  return (
    <div className={`chat-message ${message.user == "gpt" && "chatgpt"}`}>
      <div className="chat-message-center">
        <div className={`avatar ${message.user === "gpt" && "chatgpt"}`}></div>
        <div className="message" style={{ whiteSpace: "pre-wrap" }}>
          <p>{convertToLinks(message.message)}</p>
        </div>
      </div>
    </div>
  );
};


export default App;