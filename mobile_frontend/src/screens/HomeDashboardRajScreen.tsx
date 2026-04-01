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
import { ScreenNavigationProps, AppTab } from '../types';
import { colors } from '../theme/colors';
import { getScale, rs } from '../theme/layout';

type MaterialIconName = React.ComponentProps<typeof MaterialIcons>['name'];

const reminders = [
  {
    title: 'Morning Medications',
    time: '8:00 AM',
    icon: 'medication' as MaterialIconName,
    highlighted: false,
  },
  {
    title: 'Drink Water',
    time: 'Now',
    icon: 'water-drop' as MaterialIconName,
    highlighted: true,
  },
  {
    title: 'ARIA Check-in Call',
    time: '12:30 PM',
    icon: 'phone-in-talk' as MaterialIconName,
    highlighted: false,
  },
];

const moodButtons = [
  { label: 'Good', icon: 'sentiment-satisfied' as MaterialIconName },
  { label: 'Alright', icon: 'sentiment-neutral' as MaterialIconName },
  { label: 'Not great', icon: 'sentiment-dissatisfied' as MaterialIconName },
];

const avatarUri =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuC8XgiKpXfVZ04ywkMY3TycoJXpSXO3QTQG6saWNgxBBK7sMc3D6BNtbDx875cVM4OIq7xp6eVnwbCm4vpAruDyfzpDT8_phKGkf60rLoILBbmFxtYYrFCF6Di3LwFoE3DCFj4DVU_Q-_pLp_5yxtT3rgQAgQOAFFqj2ubK08j78jFC_YdXpVvmBF6YcU5GiMPCf9XyFhT1-9ssSCjxQKuGMTlAWje0gH0yEHbhqrr1b3We6F4v4IUMyFkQo0tfovFBWVTPd5_PKLA';

const HomeDashboardRajScreen = ({
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
          color={isActive ? colors.secondary : '#57534e'}
        />
        <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>{label}</Text>
      </Pressable>
    );
  };

  return (
    <View style={styles.screen}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.topAppBar}>
          <Text style={styles.greeting} numberOfLines={2}>
            Good afternoon, Raj
          </Text>
          <View style={styles.avatarWrap}>
            <Image source={{ uri: avatarUri }} style={styles.avatar} />
          </View>
        </View>

        <View style={styles.movementCard}>
          <View style={styles.movementTopRow}>
            <View style={styles.movementTextWrap}>
              <Text style={styles.sectionTitle}>Movement Safety Today</Text>
              <Text style={styles.sectionSubtitle}>
                Your movement patterns look normal today.
              </Text>
            </View>
            <View style={styles.iconTile}>
              <MaterialIcons name="track-changes" size={rs(24, scale)} color={colors.secondary} />
            </View>
          </View>

          <View style={styles.gaugeContainer}>
            <View style={styles.gaugeTrack} />
            <View style={styles.gaugeValue} />
            <Text style={styles.gaugeText}>GOOD</Text>
          </View>
        </View>

        <View style={styles.sectionSpacing}>
          <Text style={styles.sectionTitle}>Daily Reminders</Text>
          {reminders.map((item, index) => (
            <View
              key={item.title}
              style={[
                styles.reminderCard,
                index > 0 && styles.reminderGap,
                item.highlighted && styles.reminderCardHighlighted,
              ]}
            >
              <View style={styles.reminderLeft}>
                <View
                  style={[
                    styles.reminderIconBubble,
                    item.highlighted && styles.reminderIconBubbleHighlighted,
                  ]}
                >
                  <MaterialIcons
                    name={item.icon}
                    size={rs(20, scale)}
                    color={item.highlighted ? colors.white : colors.primary}
                  />
                </View>
                <View style={styles.reminderTextWrap}>
                  <Text
                    style={[
                      styles.reminderTitle,
                      item.highlighted && styles.reminderTitleHighlighted,
                    ]}
                    numberOfLines={2}
                  >
                    {item.title}
                  </Text>
                  <Text
                    style={[
                      styles.reminderTime,
                      item.highlighted && styles.reminderTimeHighlighted,
                    ]}
                  >
                    {item.time}
                  </Text>
                </View>
              </View>
              <MaterialIcons
                name={item.highlighted ? 'error' : 'chevron-right'}
                size={rs(22, scale)}
                color={item.highlighted ? colors.secondary : colors.outline}
              />
            </View>
          ))}
        </View>

        <View style={styles.moodCard}>
          <Text style={styles.moodHeading}>How are you feeling right now?</Text>
          <View style={styles.moodGrid}>
            {moodButtons.map((item) => (
              <Pressable key={item.label} style={styles.moodButton}>
                <MaterialIcons name={item.icon} size={rs(32, scale)} color={colors.primary} />
                <Text style={styles.moodButtonLabel} numberOfLines={2}>
                  {item.label}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>
      </ScrollView>

      <View style={styles.floatingMicWrap}>
        <Pressable style={styles.floatingMicBtn}>
          <MaterialIcons name="mic" size={rs(30, scale)} color={colors.white} />
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

const createStyles = (scale: number, isCompact: boolean, isTall: boolean) =>
  StyleSheet.create({
    screen: {
      flex: 1,
      backgroundColor: colors.surface,
    },
    content: {
      paddingHorizontal: rs(16, scale),
      paddingTop: rs(8, scale),
      paddingBottom: isTall ? rs(180, scale) : rs(166, scale),
      gap: rs(16, scale),
    },
    topAppBar: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingVertical: rs(8, scale),
      gap: rs(10, scale),
    },
    greeting: {
      flex: 1,
      paddingRight: rs(8, scale),
      fontSize: rs(isCompact ? 22 : 24, scale),
      lineHeight: rs(isCompact ? 28 : 30, scale),
      fontWeight: '700',
      color: colors.primary,
    },
    avatarWrap: {
      height: rs(48, scale),
      width: rs(48, scale),
      borderRadius: rs(24, scale),
      overflow: 'hidden',
      borderWidth: 2,
      borderColor: colors.secondaryContainer,
    },
    avatar: {
      width: '100%',
      height: '100%',
    },
    movementCard: {
      backgroundColor: colors.surfaceContainerLow,
      borderRadius: rs(14, scale),
      padding: rs(16, scale),
      gap: rs(12, scale),
    },
    movementTopRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      gap: rs(10, scale),
    },
    movementTextWrap: {
      flex: 1,
    },
    sectionTitle: {
      fontSize: rs(isCompact ? 20 : 22, scale),
      lineHeight: rs(isCompact ? 26 : 28, scale),
      fontWeight: '700',
      color: colors.primary,
      marginBottom: rs(2, scale),
    },
    sectionSubtitle: {
      fontSize: rs(14, scale),
      lineHeight: rs(20, scale),
      color: colors.onSurfaceVariant,
    },
    iconTile: {
      backgroundColor: 'rgba(182, 235, 219, 0.35)',
      borderRadius: rs(10, scale),
      padding: rs(8, scale),
    },
    gaugeContainer: {
      alignItems: 'center',
      justifyContent: 'flex-end',
      height: rs(102, scale),
    },
    gaugeTrack: {
      position: 'absolute',
      top: rs(8, scale),
      width: rs(198, scale),
      height: rs(96, scale),
      borderTopWidth: rs(8, scale),
      borderLeftWidth: rs(8, scale),
      borderRightWidth: rs(8, scale),
      borderColor: colors.surfaceVariant,
      borderTopLeftRadius: rs(120, scale),
      borderTopRightRadius: rs(120, scale),
    },
    gaugeValue: {
      position: 'absolute',
      top: rs(8, scale),
      width: rs(170, scale),
      height: rs(96, scale),
      borderTopWidth: rs(8, scale),
      borderLeftWidth: rs(8, scale),
      borderRightWidth: rs(8, scale),
      borderColor: colors.secondary,
      borderTopLeftRadius: rs(120, scale),
      borderTopRightRadius: rs(120, scale),
    },
    gaugeText: {
      fontSize: rs(30, scale),
      fontWeight: '800',
      color: colors.secondary,
      letterSpacing: 1,
    },
    sectionSpacing: {
      gap: rs(8, scale),
    },
    reminderCard: {
      backgroundColor: colors.surfaceContainerLowest,
      borderRadius: rs(12, scale),
      minHeight: rs(74, scale),
      paddingHorizontal: rs(12, scale),
      paddingVertical: rs(10, scale),
      borderWidth: 1,
      borderColor: 'rgba(115, 119, 127, 0.15)',
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    reminderGap: {
      marginTop: rs(6, scale),
    },
    reminderCardHighlighted: {
      backgroundColor: 'rgba(182, 235, 219, 0.40)',
      borderColor: 'rgba(53, 103, 91, 0.25)',
    },
    reminderLeft: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
      marginRight: rs(8, scale),
      gap: rs(10, scale),
    },
    reminderTextWrap: {
      flex: 1,
    },
    reminderIconBubble: {
      backgroundColor: 'rgba(0, 36, 68, 0.08)',
      width: rs(42, scale),
      height: rs(42, scale),
      borderRadius: rs(21, scale),
      alignItems: 'center',
      justifyContent: 'center',
    },
    reminderIconBubbleHighlighted: {
      backgroundColor: colors.secondary,
    },
    reminderTitle: {
      fontSize: rs(15, scale),
      lineHeight: rs(20, scale),
      fontWeight: '700',
      color: colors.onSurface,
    },
    reminderTitleHighlighted: {
      color: '#1b4f44',
    },
    reminderTime: {
      marginTop: rs(1, scale),
      fontSize: rs(13, scale),
      color: colors.onSurfaceVariant,
    },
    reminderTimeHighlighted: {
      color: colors.secondary,
      fontWeight: '700',
    },
    moodCard: {
      backgroundColor: colors.surfaceContainerHigh,
      borderRadius: rs(14, scale),
      padding: rs(16, scale),
      gap: rs(12, scale),
    },
    moodHeading: {
      fontSize: rs(isCompact ? 18 : 20, scale),
      lineHeight: rs(isCompact ? 24 : 26, scale),
      fontWeight: '700',
      color: colors.primary,
      textAlign: 'center',
    },
    moodGrid: {
      flexDirection: 'row',
      gap: rs(8, scale),
    },
    moodButton: {
      flex: 1,
      backgroundColor: colors.surfaceContainerLowest,
      borderRadius: rs(12, scale),
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: rs(96, scale),
      paddingVertical: rs(12, scale),
      paddingHorizontal: rs(6, scale),
      gap: rs(5, scale),
      borderBottomWidth: 3,
      borderBottomColor: 'transparent',
    },
    moodButtonLabel: {
      fontSize: rs(13, scale),
      lineHeight: rs(17, scale),
      textAlign: 'center',
      fontWeight: '700',
      color: colors.onSurface,
    },
    floatingMicWrap: {
      position: 'absolute',
      right: rs(14, scale),
      bottom: isTall ? rs(116, scale) : rs(106, scale),
      alignItems: 'center',
      gap: rs(5, scale),
    },
    floatingMicBtn: {
      width: rs(68, scale),
      height: rs(68, scale),
      borderRadius: rs(34, scale),
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colors.primary,
      shadowColor: '#002444',
      shadowOpacity: 0.24,
      shadowRadius: 10,
      shadowOffset: { width: 0, height: 6 },
      elevation: 8,
    },
    floatingMicLabel: {
      fontSize: rs(11, scale),
      maxWidth: rs(84, scale),
      textAlign: 'center',
      fontWeight: '700',
      color: colors.primary,
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

export default HomeDashboardRajScreen;
