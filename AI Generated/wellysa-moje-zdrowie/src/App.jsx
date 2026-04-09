import Header from './components/Header'
import Hero from './components/Hero'
import PanelUslugSection from './components/PanelUslugSection'
import WhyAndHowSection from './components/WhyAndHowSection'
import FinalCTA from './components/FinalCTA'

function App() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <Hero />
        <PanelUslugSection />
        <WhyAndHowSection />
        <FinalCTA />
      </main>
    </div>
  )
}

export default App
