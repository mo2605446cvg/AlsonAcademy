import React, { useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { UserContext } from './context/UserContext';
import LoginScreen from './screens/LoginScreen';
import HomeScreen from './screens/HomeScreen';
import UserManagement from './screens/UserManagement';
import ContentUpload from './screens/ContentUpload';
import ContentList from './screens/ContentList';
import Chat from './screens/Chat';
import Profile from './screens/Profile';
import Results from './screens/Results';
import Help from './screens/Help';

const Stack = createNativeStackNavigator();

const App = () => {
  const [user, setUser] = useState(null);

  const login = (userData) => setUser(userData);
  const logout = () => setUser(null);

  return (
    <UserContext.Provider value={{ user, login, logout }}>
      <NavigationContainer>
        <Stack.Navigator initialRouteName={user ? 'Home' : 'Login'}>
          <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
          <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
          <Stack.Screen name="UserManagement" component={UserManagement} options={{ headerShown: false }} />
          <Stack.Screen name="ContentUpload" component={ContentUpload} options={{ headerShown: false }} />
          <Stack.Screen name="Content" component={ContentList} options={{ headerShown: false }} />
          <Stack.Screen name="Chat" component={Chat} options={{ headerShown: false }} />
          <Stack.Screen name="Profile" component={Profile} options={{ headerShown: false }} />
          <Stack.Screen name="Results" component={Results} options={{ headerShown: false }} />
          <Stack.Screen name="Help" component={Help} options={{ headerShown: false }} />
        </Stack.Navigator>
      </NavigationContainer>
    </UserContext.Provider>
  );
};

export default App;