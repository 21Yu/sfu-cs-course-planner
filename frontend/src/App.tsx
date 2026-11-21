import { useState } from 'react'
import './App.css'
import { Planner } from './components/planner/Planner'
import { concentrations } from './components/planner/constants'
import {
  formatTermLabel,
  getPlannedCoursesCount,
  getPlannedUnits,
  isCoursePlanned,
  termKey,
} from './components/planner/plannerUtils'
import type { SemesterCourses } from './components/planner/types'
import { ProgressRail } from './components/ProgressRail'
import { SearchPanel } from './components/SearchPanel'
import { CourseContextProvider } from './contexts/CourseContext'
import type { Course } from './types/course'

function Dashboard() {
  const [activeConcentration, setActiveConcentration] = useState(concentrations[0])
  const [years, setYears] = useState([1, 2, 3, 4])
  const [selectedTerm, setSelectedTerm] = useState(termKey(1, 'Fall'))
  const [plannedCourses, setPlannedCourses] = useState<SemesterCourses>({})
  const [plannerMessage, setPlannerMessage] = useState<string | null>(null)

  const handleSelectCourse = (course: Course) => {
    if (isCoursePlanned(plannedCourses, course.id)) {
      setPlannerMessage(`${course.courseCode} is already in your plan.`)
      return
    }

    setPlannedCourses((current) => ({
      ...current,
      [selectedTerm]: [...(current[selectedTerm] ?? []), course],
    }))
    setPlannerMessage(
      `${course.courseCode} was added to ${formatTermLabel(selectedTerm)}.`,
    )
  }

  const handleRemoveCourse = (semesterKey: string, courseId: string) => {
    setPlannedCourses((current) => ({
      ...current,
      [semesterKey]: (current[semesterKey] ?? []).filter(
        (course) => course.id !== courseId,
      ),
    }))
  }

  const handleMoveCourse = (
    fromTerm: string,
    toTerm: string,
    courseId: string,
  ) => {
    if (!toTerm || fromTerm === toTerm) return

    setPlannedCourses((current) => {
      const courseToMove = (current[fromTerm] ?? []).find(
        (course) => course.id === courseId,
      )

      if (!courseToMove) return current

      const destinationCourses = current[toTerm] ?? []

      if (destinationCourses.some((course) => course.id === courseToMove.id)) {
        return current
      }

      return {
        ...current,
        [fromTerm]: (current[fromTerm] ?? []).filter(
          (course) => course.id !== courseId,
        ),
        [toTerm]: [...destinationCourses, courseToMove],
      }
    })
  }

  const addYear = () => {
    setYears((currentYears) => [...currentYears, currentYears.length + 1])
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#planner" aria-label="SFU CS Course Planner home">
          <span className="brand-mark" aria-hidden="true">C</span>
          <span className="brand-copy">
            <span className="brand-name">Course Planner</span>
            <span className="brand-school">SFU Computing Science</span>
          </span>
        </a>
        <div className="topbar-actions">
          <span className="save-state"><span aria-hidden="true" />Draft plan</span>
        </div>
      </header>

      <div className="workspace">
        <ProgressRail plannedUnits={getPlannedUnits(plannedCourses)} />
        <Planner
          activeConcentration={activeConcentration}
          years={years}
          selectedTerm={selectedTerm}
          plannedCourses={plannedCourses}
          message={plannerMessage}
          onSelectConcentration={setActiveConcentration}
          onSelectTerm={setSelectedTerm}
          onAddYear={addYear}
          onMoveCourse={handleMoveCourse}
          onRemoveCourse={handleRemoveCourse}
        />
        <SearchPanel
          selectedTerm={selectedTerm}
          plannedCoursesCount={getPlannedCoursesCount(plannedCourses)}
          onSelectCourse={handleSelectCourse}
        />
      </div>
    </main>
  )
}

function App() {
  return (
    <CourseContextProvider>
      <Dashboard />
    </CourseContextProvider>
  )
}

export default App
