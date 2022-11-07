/* eslint-disable prettier/prettier */
import {useNavigation} from '@react-navigation/native';
import React, {useEffect, useState} from 'react';
import {FlatList, View, Text, StyleSheet} from 'react-native';
import {Card, FAB} from 'react-native-paper';

export default function ShowFeature({}) {
  const navigation = useNavigation();
  const [data, setData] = useState([]);
  const [loading, setIsLoading] = useState(true)
  const loadData = () => {
    fetch('http://10.0.2.2:5000/get', {
      method: 'GET',
    })
      .then(resp => resp.json())
      .then(invoice => {
        setData(invoice);
        setIsLoading(false)
      });
  }

  useEffect(() => {
    loadData();
  });
  const updateScreen = (id, amount, date) => {
    navigation.navigate('Update', {
      invoice_id: id,
      total_amount: amount,
      date: date,
    });
  };
  const renderData = item => {
    return (
      <Card
        style={styles.cardStyle}
        onPress={() => {
          updateScreen(item.invoice_id, item.total_amount, item.date);
        }}>
        <Text style={{fontSize: 23}}>{item.invoice_id}</Text>
        <Text>{item.total_amount}</Text>
        <FAB
          style={styles.butStyle}
          theme={{colors: {accent: 'green'}}}
          icon="delete"
        />
      </Card>
    );
  };
  return (
    <View style={{flex: 1}}>
      <FlatList
        data={data}
        renderItem={({item}) => {
          return renderData(item);
        }}
        onRefresh = {
          () => loadData()
        }
        refreshing = {loading}
        keyExtractor={item => '${item.invoice_id}'}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  cardStyle: {
    margin: 10,
    padding: 10,
  },
  butStyle: {
    position: 'absolute',

    right: 0,
    bottom: -5,
  },
});
