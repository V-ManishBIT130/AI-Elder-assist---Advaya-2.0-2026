import React, { useState } from 'react';
import { StatusBar, StyleSheet } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import EmergencyRajScreen from './src/screens/EmergencyRajScreen';
import HomeDashboardRajScreen from './src/screens/HomeDashboardRajScreen';
import MedicationsRajScreen from './src/screens/MedicationsRajScreen';
import { AppTab } from './src/types';

const App = () => {
  const [activeTab, setActiveTab] = useState<AppTab>('home');

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="dark-content" backgroundColor="#fcf9f4" />
        {activeTab === 'home' && (
          <HomeDashboardRajScreen activeTab={activeTab} onNavigate={setActiveTab} />
        )}
        {activeTab === 'medications' && (
          <MedicationsRajScreen activeTab={activeTab} onNavigate={setActiveTab} />
        )}
        {activeTab === 'emergency' && (
          <EmergencyRajScreen activeTab={activeTab} onNavigate={setActiveTab} />
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fcf9f4',
  },
});

export default App;
