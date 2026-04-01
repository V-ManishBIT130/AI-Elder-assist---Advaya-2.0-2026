import React, { useMemo } from 'react';
import {
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
  useWindowDimensions,
} from 'react-native';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { AppTab, ScreenNavigationProps } from '../types';
import { colors } from '../theme/colors';
import { getScale, rs } from '../theme/layout';

type MaterialIconName = React.ComponentProps<typeof MaterialIcons>['name'];

type Contact = {
  initials: string;
  name: string;
  relation: string;
  bubbleColor: string;
  textColor: string;
};

const contacts: Contact[] = [
  {
    initials: 'SC',
    name: 'Sarah Chen',
    relation: 'Daughter',
    bubbleColor: colors.secondaryContainer,
    textColor: '#1b4f44',
  },
  {
    initials: 'RM',
    name: 'Dr. Rajan Mehta',
    relation: 'Doctor',
    bubbleColor: '#d2e4ff',
    textColor: '#001c38',
  },
];

const avatarUri =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuBgPwXP2w9ZfpTT_MFvMAO5W4vjj9WPTnFYhETIfwTVmNmHiFzDDOuIX1zqEVNs5KMWlilbVYKL1i9iGwwKdCvkWEBLqycEMiDP1n4Ad2ljI7pv85KJCYSBQGYI0HWQV2bJ7Egxm3xmVHLx3L76XJgUE5gfoI0Z_ISkfQ1-SXwQ8-9eky04ZfVGbd269YcUQXSPjHRD-8RV03yY-TwJ1H4bh0dMKLaNa-sP_S3Wh2EWPcDxNHCgy2b91Dc3fqcqMq4B1G0LvoseJec';

const EmergencyRajScreen = ({
  activeTab,
  onNavigate,
}: ScreenNavigationProps) => {
  const { width, height } = useWindowDimensions();
  const scale = getScale(width);
  const isCompact = width < 380;
  const isTall = height / width > 1.95;
  const styles = useMemo(() => createStyles(scale, isCompact, isTall), [scale, isCompact, isTall]);

  const renderNavItem = (icon: MaterialIconName, label: string, tab: AppTab) => {
    const isActive = activeTab === tab;

    return (
      <Pressable
        key={tab}
        onPress={() => onNavigate(tab)}
        style={[styles.navItem, isActive && styles.navItemActive]}
      >
        <MaterialIcons
          name={icon}
          size={rs(22, scale)}
          color={isActive ? '#396c5f' : '#57534e'}
        />
        <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>{label}</Text>
      </Pressable>
    );
  };

  return (
    <View style={styles.screen}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.topAppBar}>
          <View style={styles.topLeft}>
            <View style={styles.avatarWrap}>
              <Image source={{ uri: avatarUri }} style={styles.avatar} />
            </View>
            <View style={styles.titleWrap}>
              <Text style={styles.heading}>Emergency</Text>
              <Text style={styles.subtitle} numberOfLines={2}>Your help contacts are ready</Text>
            </View>
          </View>

          <Pressable style={styles.settingsBtn}>
            <MaterialIcons name="settings" size={rs(24, scale)} color={colors.onSurface} />
          </Pressable>
        </View>

        <View style={styles.contactsList}>
          {contacts.map((contact) => (
            <View key={contact.name} style={styles.contactCard}>
              <View style={styles.contactLeft}>
                <View style={[styles.initialsBubble, { backgroundColor: contact.bubbleColor }]}>
                  <Text style={[styles.initialsText, { color: contact.textColor }]}>
                    {contact.initials}
                  </Text>
                </View>
                <View style={styles.contactInfoWrap}>
                  <Text style={styles.contactName} numberOfLines={1}>{contact.name}</Text>
                  <Text style={styles.contactRole}>{contact.relation}</Text>
                </View>
              </View>

              <Pressable style={styles.callBtn}>
                <MaterialIcons name="call" size={rs(22, scale)} color={colors.white} />
              </Pressable>
            </View>
          ))}
        </View>

        <View style={styles.emergencySection}>
          <Pressable style={styles.helpBtnOuter}>
            <View style={styles.helpBtnMiddle}>
              <View style={styles.helpBtnInner}>
                <MaterialIcons name="local-hospital" size={rs(44, scale)} color={colors.white} />
                <Text style={styles.helpBtnTitle}>I NEED HELP</Text>
                <Text style={styles.helpBtnSub}>Tap once to call for help</Text>
              </View>
            </View>
          </Pressable>

          <Pressable style={styles.cancelBtn}>
            <Text style={styles.cancelText}>Cancel - I'm okay</Text>
          </Pressable>

          <View style={styles.reassuranceWrap}>
            <View style={styles.dotsRow}>
              <View style={styles.dot} />
              <View style={styles.dot} />
              <View style={styles.dot} />
            </View>
            <Text style={styles.reassuranceText}>
              "ARIA is watching over you. You are not alone."
            </Text>
          </View>
        </View>
      </ScrollView>

      <View style={styles.floatingMicWrap}>
        <Pressable style={styles.floatingMicBtn}>
          <MaterialIcons name="mic" size={rs(28, scale)} color={colors.white} />
        </Pressable>
        <Text style={styles.floatingMicLabel}>Talk to ARIA</Text>
      </View>

      <View style={styles.bottomNav}>
        {renderNavItem('home', 'Home', 'home')}
        {renderNavItem('medical-services', 'Medications', 'medications')}
        {renderNavItem('emergency', 'Emergency', 'emergency')}
      </View>
    </View>
  );
};

const createStyles = (scale: number, isCompact: boolean, isTall: boolean) => {
  const outerSize = rs(isCompact ? 194 : 214, scale);
  const middleSize = rs(isCompact ? 174 : 192, scale);
  const innerSize = rs(isCompact ? 154 : 170, scale);

  return StyleSheet.create({
    screen: {
      flex: 1,
      backgroundColor: '#fff5f5',
    },
    content: {
      paddingHorizontal: rs(16, scale),
      paddingTop: rs(8, scale),
      paddingBottom: isTall ? rs(196, scale) : rs(178, scale),
      gap: rs(14, scale),
    },
    topAppBar: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: rs(10, scale),
    },
    topLeft: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: rs(8, scale),
      flex: 1,
      paddingRight: rs(6, scale),
    },
    titleWrap: {
      flex: 1,
    },
    avatarWrap: {
      width: rs(46, scale),
      height: rs(46, scale),
      borderRadius: rs(23, scale),
      overflow: 'hidden',
      borderWidth: 2,
      borderColor: colors.primaryContainer,
    },
    avatar: {
      width: '100%',
      height: '100%',
    },
    heading: {
      fontSize: rs(isCompact ? 24 : 26, scale),
      lineHeight: rs(isCompact ? 30 : 32, scale),
      fontWeight: '700',
      color: colors.error,
    },
    subtitle: {
      marginTop: rs(1, scale),
      fontSize: rs(13, scale),
      lineHeight: rs(17, scale),
      color: colors.onSurfaceVariant,
      fontWeight: '500',
    },
    settingsBtn: {
      width: rs(42, scale),
      height: rs(42, scale),
      borderRadius: rs(21, scale),
      alignItems: 'center',
      justifyContent: 'center',
    },
    contactsList: {
      gap: rs(10, scale),
    },
    contactCard: {
      backgroundColor: colors.surfaceContainerLowest,
      borderRadius: rs(14, scale),
      padding: rs(12, scale),
      shadowColor: '#1c1c19',
      shadowOpacity: 0.08,
      shadowRadius: 10,
      shadowOffset: { width: 0, height: 6 },
      elevation: 6,
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: rs(8, scale),
    },
    contactLeft: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: rs(10, scale),
      flex: 1,
      marginRight: rs(6, scale),
    },
    contactInfoWrap: {
      flex: 1,
    },
    initialsBubble: {
      width: rs(48, scale),
      height: rs(48, scale),
      borderRadius: rs(24, scale),
      alignItems: 'center',
      justifyContent: 'center',
    },
    initialsText: {
      fontSize: rs(17, scale),
      fontWeight: '700',
    },
    contactName: {
      color: colors.primary,
      fontSize: rs(17, scale),
      lineHeight: rs(22, scale),
      fontWeight: '600',
    },
    contactRole: {
      marginTop: rs(1, scale),
      color: colors.onSurfaceVariant,
      fontSize: rs(13, scale),
      lineHeight: rs(17, scale),
    },
    callBtn: {
      width: rs(54, scale),
      height: rs(54, scale),
      borderRadius: rs(27, scale),
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    emergencySection: {
      alignItems: 'center',
      paddingTop: rs(4, scale),
    },
    helpBtnOuter: {
      width: outerSize,
      height: outerSize,
      borderRadius: outerSize / 2,
      backgroundColor: 'rgba(186, 26, 26, 0.10)',
      alignItems: 'center',
      justifyContent: 'center',
    },
    helpBtnMiddle: {
      width: middleSize,
      height: middleSize,
      borderRadius: middleSize / 2,
      backgroundColor: 'rgba(186, 26, 26, 0.08)',
      alignItems: 'center',
      justifyContent: 'center',
    },
    helpBtnInner: {
      width: innerSize,
      height: innerSize,
      borderRadius: innerSize / 2,
      backgroundColor: colors.error,
      alignItems: 'center',
      justifyContent: 'center',
      paddingHorizontal: rs(10, scale),
    },
    helpBtnTitle: {
      color: colors.white,
      fontWeight: '800',
      fontSize: rs(18, scale),
      letterSpacing: 0.6,
      marginTop: rs(4, scale),
      textAlign: 'center',
    },
    helpBtnSub: {
      marginTop: rs(2, scale),
      color: colors.white,
      opacity: 0.95,
      fontSize: rs(10, scale),
      textTransform: 'uppercase',
      lineHeight: rs(14, scale),
      textAlign: 'center',
      maxWidth: '82%',
    },
    cancelBtn: {
      marginTop: rs(16, scale),
      backgroundColor: colors.surfaceContainerHigh,
      borderRadius: rs(12, scale),
      paddingHorizontal: rs(22, scale),
      paddingVertical: rs(12, scale),
    },
    cancelText: {
      fontSize: rs(16, scale),
      fontWeight: '700',
      color: colors.onSurface,
    },
    reassuranceWrap: {
      marginTop: rs(22, scale),
      alignItems: 'center',
      paddingHorizontal: rs(10, scale),
      maxWidth: rs(300, scale),
    },
    dotsRow: {
      flexDirection: 'row',
      gap: rs(6, scale),
      marginBottom: rs(8, scale),
    },
    dot: {
      width: rs(7, scale),
      height: rs(7, scale),
      borderRadius: rs(3.5, scale),
      backgroundColor: colors.secondary,
    },
    reassuranceText: {
      color: colors.primary,
      fontSize: rs(15, scale),
      textAlign: 'center',
      fontStyle: 'italic',
      lineHeight: rs(22, scale),
      opacity: 0.82,
    },
    floatingMicWrap: {
      position: 'absolute',
      right: rs(14, scale),
      bottom: isTall ? rs(116, scale) : rs(106, scale),
      alignItems: 'center',
      gap: rs(4, scale),
    },
    floatingMicBtn: {
      width: rs(66, scale),
      height: rs(66, scale),
      borderRadius: rs(33, scale),
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
      elevation: 8,
    },
    floatingMicLabel: {
      fontSize: rs(10, scale),
      maxWidth: rs(80, scale),
      textAlign: 'center',
      color: colors.primary,
      fontWeight: '700',
      textTransform: 'uppercase',
      letterSpacing: 0.6,
    },
    bottomNav: {
      position: 'absolute',
      left: 0,
      right: 0,
      bottom: 0,
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: rs(8, scale),
      paddingBottom: isTall ? rs(16, scale) : rs(12, scale),
      paddingHorizontal: rs(8, scale),
      borderTopLeftRadius: rs(22, scale),
      borderTopRightRadius: rs(22, scale),
      backgroundColor: colors.surface,
      shadowColor: '#1c1c19',
      shadowOpacity: 0.09,
      shadowRadius: 10,
      shadowOffset: { width: 0, height: -5 },
      elevation: 14,
    },
    navItem: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 999,
      paddingHorizontal: rs(6, scale),
      paddingVertical: rs(8, scale),
      marginHorizontal: rs(3, scale),
    },
    navItemActive: {
      backgroundColor: colors.secondaryContainer,
    },
    navLabel: {
      marginTop: rs(3, scale),
      fontSize: rs(11, scale),
      textAlign: 'center',
      fontWeight: '700',
      color: '#57534e',
    },
    navLabelActive: {
      color: '#396c5f',
    },
  });
};

export default EmergencyRajScreen;
