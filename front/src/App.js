import './App.css';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import 'semantic-ui-css/semantic.min.css'
import Home from './components/Home'


function App() {
  return (
    <div>
      <Home className="Home"></Home>
    </div>
  );
}

export default App;

/*<Router>
      <Route exact path="/" component={Home}></Route>
    </Router>*/
