import { useState } from 'react'
import './App.css'
import { CourseSearch } from './components/CourseSearch/CourseSearch'
import { CourseContextProvider } from './contexts/CourseContext'
import type { Course } from './types/course'

const concentrations = [
  'Artificial Intelligence',
  'Visual & Interactive Computing',
  'Computing Systems',
  'Information Systems',
  'Programming Languages & Software',
  'Theoretical Computing Science',
]

const terms = ['Fall', 'Spring', 'Summer'] as const

type Term = (typeof terms)[number]
type SemesterCourses = Record<string, Course[]>
type SemesterOption = { key: string; label: string }

const termKey = (year: number, term: Term) =>
  `year-${year}-${term.toLowerCase()}`

const formatTermLabel = (key: string) => {
  const [, year, term] = key.split('-')
  return `Year ${year} · ${term[0].toUpperCase()}${term.slice(1)}`
}

const termDates: Record<Term, string> = {
  Fall: 'Sep – Dec',
  Spring: 'Jan – Apr',
  Summer: 'May – Aug',
}

const getTotalUnits = (courses: Course[]) =>
  courses.reduce((total, course) => total + course.credits, 0)

const getPlannedCoursesCount = (plannedCourses: SemesterCourses) =>
  Object.values(plannedCourses).flat().length

const getPlannedUnits = (plannedCourses: SemesterCourses) =>
  getTotalUnits(Object.values(plannedCourses).flat())

const getSemesterOptions = (years: number[]): SemesterOption[] =>
  years.flatMap((year) =>
    terms.map((term) => {
      const key = termKey(year, term)
      return { key, label: formatTermLabel(key) }
    }),
  )

const isCoursePlanned = (plannedCourses: SemesterCourses, courseId: string) =>
  Object.values(plannedCourses)
    .flat()
    .some((course) => course.id === courseId)

function ProgressRail({ plannedUnits }: { plannedUnits: number }) {
  const progress = Math.min((plannedUnits / 120) * 100, 100)

  return (
    <aside className="progress-rail" aria-labelledby="progress-heading">
      <div className="rail-heading">
        <p className="section-kicker">Your degree</p>
        <h1 id="progress-heading">Progress</h1>
        <p className="rail-description">
          A snapshot of your path to graduation.
        </p>
      </div>

      <section className="degree-card" aria-label="Degree progress summary">
        <div className="degree-card-top">
          <span className="degree-icon" aria-hidden="true">✦</span>
          <span className="degree-label">Computing Science</span>
        </div>
        <div className="credit-count">
          <strong>{plannedUnits}</strong>
          <span>units planned</span>
        </div>
        <div
          className="progress-track"
          role="progressbar"
          aria-label="Degree units planned"
          aria-valuenow={Math.min(plannedUnits, 120)}
          aria-valuemin={0}
          aria-valuemax={120}
        >
          <span style={{ width: `${progress}%` }} />
        </div>
        <p className="degree-footnote">Add courses to see your progress here.</p>
      </section>

      <section className="requirements" aria-labelledby="requirements-heading">
        <div className="section-title-row">
          <h2 id="requirements-heading">Requirement groups</h2>
          <button
            className="text-button"
            type="button"
            aria-label="View all degree requirements"
          >
            View all
          </button>
        </div>
        <RequirementRow icon="◈" iconClass="breadth" title="Lower division" detail="Core foundations" />
        <RequirementRow icon="⌘" iconClass="depth" title="Upper division" detail="Advanced courses" />
        <RequirementRow icon="✳" iconClass="electives" title="Electives" detail="Explore your interests" />
      </section>

      <div className="rail-tip">
        <span className="tip-icon" aria-hidden="true">✦</span>
        <p>
          <strong>Make it yours</strong>
          <br />
          Build a plan that fits your goals and pace.
        </p>
      </div>
      <p className="requirements-note">
        Requirements can vary by calendar year. Always confirm with the SFU Calendar.
      </p>
    </aside>
  )
}

function RequirementRow({
  icon,
  iconClass,
  title,
  detail,
}: {
  icon: string
  iconClass: string
  title: string
  detail: string
}) {
  return (
    <div className="requirement-row">
      <span className={`requirement-icon ${iconClass}`} aria-hidden="true">
        {icon}
      </span>
      <span className="requirement-copy">
        <strong>{title}</strong>
        <small>{detail}</small>
      </span>
      <span className="requirement-count">To track</span>
    </div>
  )
}

function TermCard({
  term,
  semesterKey,
  courses,
  isSelected,
  semesterOptions,
  onSelect,
  onMoveCourse,
  onRemoveCourse,
}: {
  term: Term
  semesterKey: string
  courses: Course[]
  isSelected: boolean
  semesterOptions: SemesterOption[]
  onSelect: (semesterKey: string) => void
  onMoveCourse: (fromTerm: string, toTerm: string, courseId: string) => void
  onRemoveCourse: (semesterKey: string, courseId: string) => void
}) {
  const units = getTotalUnits(courses)

  return (
    <section className={`term-card${isSelected ? ' selected' : ''}`}>
      <div className="term-card-heading">
        <button
          type="button"
          className="term-select-button"
          aria-pressed={isSelected}
          onClick={() => onSelect(semesterKey)}
        >
          <span>{term}</span>
          <span>{termDates[term]}</span>
        </button>
      </div>

      <div className="term-dropzone">
        {courses.length === 0 ? (
          <>
            <span className="plus-mark" aria-hidden="true">+</span>
            <span>{isSelected ? 'Selected for courses' : 'Choose term'}</span>
          </>
        ) : (
          courses.map((course) => (
            <div className="planned-course" key={course.id}>
              <span>{course.courseCode}</span>
              <select
                className="move-course-select"
                defaultValue=""
                aria-label={`Move ${course.courseCode} from ${term}`}
                onChange={(event) =>
                  onMoveCourse(semesterKey, event.target.value, course.id)
                }
              >
                <option value="" disabled>
                  Move to…
                </option>
                {semesterOptions
                  .filter((semester) => semester.key !== semesterKey)
                  .map((semester) => (
                    <option key={semester.key} value={semester.key}>
                      {semester.label}
                    </option>
                  ))}
              </select>
              <button
                type="button"
                className="remove-course-button"
                aria-label={`Remove ${course.courseCode} from ${term}`}
                onClick={() => onRemoveCourse(semesterKey, course.id)}
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>

      <div className="term-units">{units} units</div>
    </section>
  )
}

function Planner({
  activeConcentration,
  years,
  selectedTerm,
  plannedCourses,
  message,
  onSelectConcentration,
  onSelectTerm,
  onAddYear,
  onMoveCourse,
  onRemoveCourse,
}: {
  activeConcentration: string
  years: number[]
  selectedTerm: string
  plannedCourses: SemesterCourses
  message: string | null
  onSelectConcentration: (concentration: string) => void
  onSelectTerm: (semesterKey: string) => void
  onAddYear: () => void
  onMoveCourse: (fromTerm: string, toTerm: string, courseId: string) => void
  onRemoveCourse: (semesterKey: string, courseId: string) => void
}) {
  const semesterOptions = getSemesterOptions(years)

  return (
    <section className="planner" id="planner" aria-labelledby="planner-heading">
      <div className="planner-heading-row">
        <div>
          <p className="section-kicker">Your academic journey</p>
          <h2 id="planner-heading">My course plan</h2>
        </div>
        <span className="term-button">
          <span aria-hidden="true">▦</span>
          Fall 2026
          <span className="chevron" aria-hidden="true">⌄</span>
        </span>
      </div>

      <nav className="concentration-nav" aria-label="Browse concentrations">
        {concentrations.map((concentration) => (
          <button
            className={`concentration-tab${activeConcentration === concentration ? ' active' : ''}`}
            type="button"
            aria-pressed={activeConcentration === concentration}
            onClick={() => onSelectConcentration(concentration)}
            key={concentration}
          >
            {concentration}
          </button>
        ))}
      </nav>

      <div className="planner-caption">
        <span>Select a term, then add matching courses from search.</span>
        <span className="legend-button">
          <span aria-hidden="true">ⓘ</span> Click a term to choose it
        </span>
      </div>

      {message && (
        <p className="planner-message" aria-live="polite">
          {message}
        </p>
      )}

      <div className="year-list">
        {years.map((year) => (
          <section className="year-section" aria-labelledby={`year-${year}`} key={year}>
            <div className="year-label">
              <span id={`year-${year}`}>Year {year}</span>
              <span className="year-rule" />
            </div>
            <div className="term-grid">
              {terms.map((term) => {
                const semesterKey = termKey(year, term)

                return (
                  <TermCard
                    key={term}
                    term={term}
                    semesterKey={semesterKey}
                    courses={plannedCourses[semesterKey] ?? []}
                    isSelected={selectedTerm === semesterKey}
                    semesterOptions={semesterOptions}
                    onSelect={onSelectTerm}
                    onMoveCourse={onMoveCourse}
                    onRemoveCourse={onRemoveCourse}
                  />
                )
              })}
            </div>
          </section>
        ))}
      </div>

      <button className="add-year-button" type="button" onClick={onAddYear}>
        <span aria-hidden="true">+</span> Add another year
      </button>
    </section>
  )
}

function SearchPanel({
  selectedTerm,
  plannedCoursesCount,
  onSelectCourse,
}: {
  selectedTerm: string
  plannedCoursesCount: number
  onSelectCourse: (course: Course) => void
}) {
  return (
    <aside className="search-panel" aria-labelledby="search-heading">
      <div className="search-panel-heading">
        <div>
          <p className="section-kicker">Build your plan</p>
          <h2 id="search-heading">Find a course</h2>
        </div>
        <span className="search-count">{plannedCoursesCount} added</span>
      </div>
      <p className="search-target">Adding to {formatTermLabel(selectedTerm)}</p>
      <CourseSearch onSelect={onSelectCourse} />
      <div className="search-panel-footer">
        <span className="footer-sparkle" aria-hidden="true">✦</span>
        <p>Choose a term, then use Add course in a search result.</p>
      </div>
    </aside>
  )
}

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
