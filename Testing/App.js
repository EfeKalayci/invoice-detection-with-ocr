/* eslint-disable prettier/prettier */
import {StyleSheet, Text, View, Button} from 'react-native';
import HomeScreen from './screens/HomeScreen';
import AddScreen from './screens/AddScreen';
import ListScreen from './screens/ListScreen';
import ShowFeature from './components/ShowFeature';
import LookInvoice from './components/LookInvoice';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import React from 'react';

const Stack = createNativeStackNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{headerShown: false}}
        />
        <Stack.Screen name="Add" component={AddScreen} />
        <Stack.Screen name="Show" component={ShowFeature} />
        <Stack.Screen name="List" component={ListScreen} />
        <Stack.Screen name="Update" component={LookInvoice} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default App;
