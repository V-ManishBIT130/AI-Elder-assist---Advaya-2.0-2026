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

type MedicationCard = {
  time: string;
  name: string;
  status: 'taken' | 'due' | 'upcoming';
  statusLabel: string;
  supply: string;
  supplyPercent: number;
  leftBorder: string;
};

const medicationCards: MedicationCard[] = [
  {
    time: '8:00 AM',
    name: 'Metformin',
    status: 'taken',
    statusLabel: 'Taken',
    supply: '22 days left',
    supplyPercent: 70,
    leftBorder: colors.secondary,
  },
  {
    time: '1:00 PM',
    name: 'Amlodipine',
    status: 'due',
    statusLabel: 'Due Now',
    supply: '5 days left',
    supplyPercent: 15,
    leftBorder: colors.tertiaryFixedDim,
  },
  {
    time: '8:00 PM',
    name: 'Aspirin',
    status: 'upcoming',
    statusLabel: 'Upcoming',
    supply: '45 days left',
    supplyPercent: 90,
    leftBorder: colors.primary,
  },
];

const avatarUri =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuDBcRC-HuzQsFnt8oLk-hIGHqY0Bfam7UZg1fbEMP847BUh4nFzJISWdO3sXh4AblhOu5J-sm7PdC_doo7-22e7x1pJ02uhbQziwBybMGYyh4RBy2Rne1zAXOJy_8M3LZfS0ckEcEGcUW2vW_I9848A-cUJdwQIjZpjxSSFEL5zMw-OA5tYRd9yVRDWa5YJCx3kktgaiMCdzur8LooGI58UBPIoWMJhYraZn1ONnbsSQVAJ654KsWroLVpUizKvAGl7Ug7mM4Vh5mw';

const MedicationsRajScreen = ({
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
          <View style={styles.topTextWrap}>
            <Text style={styles.heading} numberOfLines={1}>Your Medicines</Text>
            <Text style={styles.subheading}>3 medicines today</Text>
          </View>
          <View style={styles.avatarWrap}>
            <Image source={{ uri: avatarUri }} style={styles.avatar} />
          </View>
        </View>

        <View style={styles.warningBanner}>
          <View style={styles.warningIconWrap}>
            <MaterialIcons name="warning" size={rs(18, scale)} color={colors.tertiary} />
          </View>
          <View style={styles.warningTextWrap}>
            <Text style={styles.warningTitle}>Check with your doctor</Text>
            <Text style={styles.warningSubtitle}>
              Aspirin + Warfarin may increase bleeding risk.
            </Text>
          </View>
        </View>

        {medicationCards.map((item) => (
          <View key={item.name} style={[styles.medCard, { borderLeftColor: item.leftBorder }]}>
            <View style={styles.medCardTop}>
              <View style={styles.medNameWrap}>
                <Text
                  style={[
                    styles.medTime,
                    item.status === 'due' && { color: colors.tertiary },
                    item.status === 'upcoming' && { color: colors.primary },
                  ]}
                >
                  {item.time}
                </Text>
                <Text style={styles.medName} numberOfLines={1}>{item.name}</Text>
              </View>

              <View
                style={[
                  styles.statusBadge,
                  item.status === 'taken' && styles.statusTaken,
                  item.status === 'due' && styles.statusDue,
                  item.status === 'upcoming' && styles.statusUpcoming,
                ]}
              >
                <MaterialIcons
                  name={
                    item.status === 'taken'
                      ? 'check-circle'
                      : item.status === 'due'
                        ? 'schedule'
                        : 'upcoming'
                  }
                  size={rs(15, scale)}
                  color={
                    item.status === 'taken'
                      ? '#1b4f44'
                      : item.status === 'due'
                        ? colors.tertiary
                        : colors.onSurfaceVariant
                  }
                />
                <Text style={styles.statusText} numberOfLines={1}>{item.statusLabel}</Text>
              </View>
            </View>

            <View style={styles.medBottom}>
              <View style={styles.supplyRow}>
                <Text style={styles.supplyLabel}>Supply Status</Text>
                <Text style={styles.supplyLabel}>{item.supply}</Text>
              </View>

              <View style={styles.progressTrack}>
                <View
                  style={[
                    styles.progressFill,
                    {
                      width: `${item.supplyPercent}%`,
                      backgroundColor:
                        item.status === 'due' ? colors.tertiaryFixedDim : item.leftBorder,
                    },
                  ]}
                />
              </View>

              <Pressable
                disabled={item.status === 'taken'}
                style={[
                  styles.takeButton,
                  item.status === 'taken' && styles.takeButtonDisabled,
                ]}
              >
                {item.status !== 'taken' && (
                  <MaterialIcons name="done" size={rs(18, scale)} color={colors.white} />
                )}
                <Text
                  style={[
                    styles.takeButtonText,
                    item.status === 'taken' && styles.takeButtonTextDisabled,
                  ]}
                  numberOfLines={1}
                >
                  {item.status === 'taken' ? 'Already taken' : 'I TOOK IT'}
                </Text>
              </Pressable>
            </View>
          </View>
        ))}
      </ScrollView>

      <View style={styles.floatingMicWrap}>
        <View style={styles.micGlow} />
        <Pressable style={styles.floatingMicBtn}>
          <MaterialIcons name="mic" size={rs(34, scale)} color={colors.white} />
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
      paddingBottom: isTall ? rs(190, scale) : rs(176, scale),
      gap: rs(12, scale),
    },
    topAppBar: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingVertical: rs(8, scale),
      gap: rs(10, scale),
    },
    topTextWrap: {
      flex: 1,
      paddingRight: rs(6, scale),
    },
    heading: {
      fontSize: rs(isCompact ? 24 : 26, scale),
      fontWeight: '700',
      color: colors.primary,
      lineHeight: rs(isCompact ? 30 : 32, scale),
    },
    subheading: {
      marginTop: rs(2, scale),
      fontSize: rs(14, scale),
      color: '#6b7280',
      fontWeight: '600',
    },
    avatarWrap: {
      width: rs(48, scale),
      height: rs(48, scale),
      borderRadius: rs(24, scale),
      overflow: 'hidden',
      borderWidth: 2,
      borderColor: colors.secondaryContainer,
    },
    avatar: {
      width: '100%',
      height: '100%',
    },
    warningBanner: {
      backgroundColor: colors.tertiaryFixed,
      borderRadius: rs(14, scale),
      borderLeftWidth: rs(6, scale),
      borderLeftColor: colors.tertiary,
      padding: rs(12, scale),
      flexDirection: 'row',
      gap: rs(10, scale),
    },
    warningIconWrap: {
      width: rs(30, scale),
      height: rs(30, scale),
      borderRadius: rs(15, scale),
      backgroundColor: colors.white,
      alignItems: 'center',
      justifyContent: 'center',
      marginTop: rs(2, scale),
    },
    warningTextWrap: {
      flex: 1,
    },
    warningTitle: {
      fontSize: rs(16, scale),
      lineHeight: rs(21, scale),
      fontWeight: '700',
      color: '#2c1700',
      marginBottom: rs(2, scale),
    },
    warningSubtitle: {
      fontSize: rs(13, scale),
      lineHeight: rs(18, scale),
      color: '#683d00',
    },
    medCard: {
      backgroundColor: colors.surfaceContainerLowest,
      borderRadius: rs(14, scale),
      borderLeftWidth: rs(8, scale),
      padding: rs(14, scale),
      minHeight: rs(190, scale),
      shadowColor: '#1c1c19',
      shadowOpacity: 0.08,
      shadowRadius: 10,
      shadowOffset: { width: 0, height: 6 },
      elevation: 6,
    },
    medCardTop: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      gap: rs(8, scale),
      marginBottom: rs(12, scale),
    },
    medNameWrap: {
      flex: 1,
      marginRight: rs(4, scale),
    },
    medTime: {
      color: colors.secondary,
      fontSize: rs(13, scale),
      fontWeight: '700',
      marginBottom: rs(2, scale),
    },
    medName: {
      color: colors.primary,
      fontSize: rs(isCompact ? 24 : 26, scale),
      fontWeight: '700',
      lineHeight: rs(isCompact ? 30 : 32, scale),
    },
    statusBadge: {
      borderRadius: 999,
      paddingHorizontal: rs(8, scale),
      paddingVertical: rs(6, scale),
      flexDirection: 'row',
      alignItems: 'center',
      gap: rs(5, scale),
      alignSelf: 'flex-start',
      maxWidth: '45%',
    },
    statusTaken: {
      backgroundColor: colors.secondaryContainer,
    },
    statusDue: {
      backgroundColor: colors.tertiaryFixed,
    },
    statusUpcoming: {
      backgroundColor: colors.surfaceContainer,
    },
    statusText: {
      fontSize: rs(11, scale),
      fontWeight: '700',
      color: colors.onSurface,
      flexShrink: 1,
    },
    medBottom: {
      marginTop: 'auto',
      gap: rs(10, scale),
    },
    supplyRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
    },
    supplyLabel: {
      color: '#6b7280',
      fontSize: rs(12, scale),
      fontWeight: '600',
    },
    progressTrack: {
      height: rs(8, scale),
      width: '100%',
      borderRadius: 999,
      overflow: 'hidden',
      backgroundColor: colors.surfaceContainer,
    },
    progressFill: {
      height: '100%',
      borderRadius: 999,
    },
    takeButton: {
      marginTop: rs(4, scale),
      minHeight: rs(46, scale),
      borderRadius: rs(10, scale),
      backgroundColor: colors.primary,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: rs(6, scale),
      paddingHorizontal: rs(10, scale),
    },
    takeButtonDisabled: {
      backgroundColor: colors.surfaceContainerHigh,
    },
    takeButtonText: {
      color: colors.white,
      fontSize: rs(16, scale),
      fontWeight: '700',
      letterSpacing: 0.2,
    },
    takeButtonTextDisabled: {
      color: '#78716c',
      fontSize: rs(15, scale),
    },
    floatingMicWrap: {
      position: 'absolute',
      right: rs(14, scale),
      bottom: isTall ? rs(116, scale) : rs(106, scale),
      alignItems: 'center',
      gap: rs(4, scale),
    },
    micGlow: {
      position: 'absolute',
      top: rs(6, scale),
      width: rs(72, scale),
      height: rs(72, scale),
      borderRadius: rs(36, scale),
      backgroundColor: colors.secondary,
      opacity: 0.18,
    },
    floatingMicBtn: {
      width: rs(72, scale),
      height: rs(72, scale),
      borderRadius: rs(36, scale),
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
      elevation: 8,
    },
    floatingMicLabel: {
      color: colors.primary,
      fontSize: rs(11, scale),
      maxWidth: rs(84, scale),
      textAlign: 'center',
      fontWeight: '700',
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

export default MedicationsRajScreen;
