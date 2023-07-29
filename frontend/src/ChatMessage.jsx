import { useState, useEffect, useRef } from 'react';
import './App.css';
import Papa from 'papaparse'
import axios from 'axios';

const ChatMessage = ({ message }) => {
    const convertToLinks = (inputString, specify_floor) => {
      //const regex = /\[(.*?),\((https:\/\/www\.google\.com\/maps\/place\/[\d\.,]+)\),(\d+)\]/g;
      const regex = /\[(.*?),\((https:\/\/www\.google\.com\/maps\/place\/[\d\.,]+)\),(.*?)\]/g;
  
      let tempText = inputString;
      let match;
  
      while ((match = regex.exec(inputString)) !== null) {
        const room = match[1];
        const url = match[2];
        const floor = match[3];
        let prefix;
        console.log(floor)
  
        if (floor === "None") {
          prefix = "_______";
        } else {
          prefix = `floor <b>${floor}</b>`
        }
        
        const link = specify_floor ? ` ${prefix}&nbsp&nbsp&nbsp->&nbsp&nbsp&nbsp<a href="${url}" target="_blank" rel="noopener noreferrer">${room}</a>` : `<a href="${url}" target="_blank" rel="noopener noreferrer">${room}</a>`;
        tempText = tempText.replace(match[0], link);
      }
  
      return tempText;
    };
  
    const createTableRows = (inputString) => {
      const lines = inputString.split('\n');
      const tableRows = lines.filter(line => isTableRow(line));
      const nonTableRows = lines.filter(line => !isTableRow(line));
      let colorState = 1;
      let prev_date = "!";
  
      const renderTable = tableRows.map((line, index) => {
        const row = Papa.parse(line, { delimiter: ',', skipEmptyLines: true }).data[0];
        const date = row[0];
        if (date !== prev_date) {
          colorState = !colorState;
        }
        prev_date = date;
  
        const columns = row.map((cell, cellIndex) => {
          const convertedCell = convertToLinks(cell, 0);
          return index == 0 ? <th key={cellIndex} dangerouslySetInnerHTML={{ __html: convertedCell }}></th> : <td key={cellIndex} dangerouslySetInnerHTML={{ __html: convertedCell }}></td>;
        });
  
        return colorState ? <tr key={index} style={{ background: "#343541" }}>{columns}</tr> : <tr key={index}>{columns}</tr>;
      });
  
      const renderNonTable = nonTableRows.map((line, index) => <p key={index} dangerouslySetInnerHTML={{ __html: convertToLinks(line,1) }}></p>);
  
      return (
        <div className="both-tables">
          <table className="message-table"><tbody>{renderTable}</tbody></table>
          <div className="non-table">{renderNonTable}</div>
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

export default ChatMessage