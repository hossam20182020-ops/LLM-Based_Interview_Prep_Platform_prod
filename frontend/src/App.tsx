import React from 'react'
import GenerateForm from './components/GenerateForm'
import QuestionList from './components/QuestionList'
import Stats from './components/Stats'

export default function App() {
  return (
    <div className='container'>
      <h1>LLM Interview Prep</h1>
      <p>Generate, save, rate, and flag interview questions for any job title.</p>
      <GenerateForm onSaved={()=>{}}/>
      <div className='grid grid-2'>
        <QuestionList />
        <Stats />
      </div>
      <footer style={{marginTop:24, fontSize:12, opacity:0.7}}>
        Built with FastAPI + React + PostgreSQL
      </footer>
    </div>
  )
}
