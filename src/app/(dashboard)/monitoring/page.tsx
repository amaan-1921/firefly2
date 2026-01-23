// src/app/(dashboard)/monitoring/page.tsx
'use client';

import {
  Card,
  CardContent,
  CardHeader,
  Button,
  Modal,
  Drawer,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider as MuiSlider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { useAlerts } from '@/hooks/useAlerts';
import { useAlertStore } from '@/store/useAlertStore';

const WorldMap = dynamic(() => import("@/components/dashboard/WorldMap"), { ssr: false });

type MonitoringState = 'idle' | 'config' | 'active';

export default function MonitoringPage() {
  const router = useRouter();
  const { monitoringConfig, setMonitoringConfig, setSelectedAlert, setSelectedAlertContext, resolvedAlerts } = useAlertStore();
  
  const [state, setState] = useState<MonitoringState>(
    monitoringConfig.isActive ? 'active' : 'idle'
  );
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [configOpen, setConfigOpen] = useState(false);
  const [selectedAlertForModal, setSelectedAlertForModal] = useState<any>(null);
  
  const [tempConfig, setTempConfig] = useState({
    riskCategory: monitoringConfig.riskCategory,
    impactThreshold: monitoringConfig.impactThreshold,
    frequency: monitoringConfig.frequency,
  });

  const {
    data: alerts = [],
    isLoading,
    isError,
    refetch,
  } = useAlerts();

  const filteredAlerts = alerts.filter((a) => {
    const categoryOk =
      tempConfig.riskCategory === 'ALL' || a.riskCategory === tempConfig.riskCategory;
    const impactOk = a.estimatedRevenueImpact >= tempConfig.impactThreshold;
    const notResolved = !resolvedAlerts.includes(a.id);
    return categoryOk && impactOk && notResolved;
  });

  const handleViewDetails = (alert: any) => {
    setSelectedAlertForModal(alert);
    setModalOpen(true);
  };

  const handleAnalyzeImpact = (alert: any) => {
    setSelectedAlert(alert);
    router.push('/impact');
  };

  const handleReasoningTraces = (alert: any) => {
    setSelectedAlertForModal(alert);
    setSelectedAlertContext({ alert, impactedPOs: [] });
    setDrawerOpen(true);
  };

  const handleSaveConfig = () => {
    setMonitoringConfig({
      riskCategory: tempConfig.riskCategory,
      impactThreshold: tempConfig.impactThreshold,
      frequency: tempConfig.frequency,
      isActive: true,
    });
    setState('active');
    setConfigOpen(false);
    refetch();
  };

  const breached = filteredAlerts.filter(
    (a) => a.severity === 'CRITICAL' || a.severity === 'HIGH'
  );
  const watchlist = filteredAlerts.filter((a) => a.severity === 'MEDIUM');
  const safe = filteredAlerts.filter((a) => a.severity === 'LOW');

  // STATE A: IDLE
  if (state === 'idle') {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 bg-white">
        <div className="w-full max-w-5xl mb-8">
                        <WorldMap alerts={filteredAlerts} />
        </div>
        <div className="text-center">
          <p className="text-lg text-slate-600 mb-6">
            System Ready. Configure filters to start monitoring.
          </p>
          <Button
            variant="contained"
            size="large"
            onClick={() => {
              setConfigOpen(true);
              setState('config');
            }}
            sx={{
              bgcolor: '#E57373',
              '&:hover': { bgcolor: '#D84315' },
              textTransform: 'none',
              fontWeight: 600,
              px: 4,
              py: 1.5,
            }}
          >
            Configure Monitoring
          </Button>
        </div>
      </div>
    );
  }

  // STATE B & C: CONFIG DIALOG + ACTIVE VIEW
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 pb-4 border-b border-slate-200 bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              Active Alerts
            </h1>
            <p className="text-sm text-slate-500">
              Threshold-based swimlanes highlighting critical attention areas
            </p>
          </div>
          <div className="flex gap-2 items-center">
            <Button
              size="small"
              variant="outlined"
              onClick={() => setConfigOpen(true)}
              sx={{ textTransform: 'none' }}
            >
              Configure
            </Button>
            {isLoading && (
              <span className="text-xs text-slate-400">Refreshing signals…</span>
            )}
          </div>
        </div>
      </div>

      {/* Configuration Dialog */}
      <Dialog
        open={configOpen}
        onClose={() => setConfigOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Configure Monitoring Parameters</DialogTitle>
        <DialogContent>
          <div className="space-y-6 pt-4">
            <FormControl fullWidth>
              <InputLabel>Risk Category</InputLabel>
              <Select
                value={tempConfig.riskCategory}
                label="Risk Category"
                onChange={(e) =>
                  setTempConfig({ ...tempConfig, riskCategory: e.target.value })
                }
              >
                <MenuItem value="ALL">All Categories</MenuItem>
                <MenuItem value="GEOPOLITICAL">Geopolitical</MenuItem>
                <MenuItem value="WEATHER">Weather</MenuItem>
                <MenuItem value="LOGISTICS">Logistics</MenuItem>
                <MenuItem value="SUPPLIER">Supplier</MenuItem>
              </Select>
            </FormControl>

            <div>
              <label className="text-sm font-medium mb-2 block text-slate-700">
                Impact Threshold: ${(tempConfig.impactThreshold / 1000).toFixed(0)}k+
              </label>
              <MuiSlider
                value={tempConfig.impactThreshold}
                onChange={(_, value) =>
                  setTempConfig({ ...tempConfig, impactThreshold: value as number })
                }
                min={100000}
                max={2000000}
                step={100000}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
            </div>

            <FormControl fullWidth>
              <InputLabel>Refresh Frequency</InputLabel>
              <Select
                value={tempConfig.frequency}
                label="Refresh Frequency"
                onChange={(e) =>
                  setTempConfig({ ...tempConfig, frequency: e.target.value })
                }
              >
                <MenuItem value="realtime">Real-time (60s)</MenuItem>
                <MenuItem value="5min">Every 5 minutes</MenuItem>
                <MenuItem value="15min">Every 15 minutes</MenuItem>
              </Select>
            </FormControl>
          </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveConfig}
            sx={{
              bgcolor: '#E57373',
              '&:hover': { bgcolor: '#D84315' },
            }}
          >
            Save & Execute
          </Button>
        </DialogActions>
      </Dialog>

      {/* STATE C: ACTIVE - Traffic Light View */}
      <div className="flex-1 overflow-y-auto bg-slate-50 p-6 space-y-6">
        {isError && (
          <p className="text-xs text-red-600">
            Failed to load monitoring data.{' '}
            <button onClick={() => refetch()} className="underline underline-offset-2">
              Retry
            </button>
          </p>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Breached / Critical */}
          <Card className="border-t-4 border-red-500 bg-red-50/50 rounded-xl shadow-sm">
            <CardHeader
              title={
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-red-600 uppercase">
                    Breached (Critical)
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {breached.length} alerts
                  </span>
                </div>
              }
            />
            <CardContent className="space-y-3">
              {breached.length === 0 && !isLoading && (
                <p className="text-xs text-slate-400">
                  No breached risks above current threshold.
                </p>
              )}
              {breached.map((alert) => (
                <div
                  key={alert.id}
                  className="rounded-lg border border-red-400 bg-white px-3 py-2 shadow-sm animate-pulse cursor-pointer hover:shadow-md transition-all"
                >
                  <p className="text-sm font-semibold text-slate-900">
                    {alert.title}
                  </p>
                  <p className="text-xs text-slate-600">
                    Impact: High ({alert.impactedPoCount} POs affected)
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Status: Critical · Last Update:{' '}
                    {new Date(alert.lastUpdatedAt).toLocaleTimeString()}
                  </p>
                  <div className="flex gap-2 mt-2">
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleViewDetails(alert)}
                      sx={{ textTransform: 'none', fontSize: '11px' }}
                    >
                      View Details
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleReasoningTraces(alert)}
                      sx={{ textTransform: 'none', fontSize: '11px' }}
                    >
                      Reasoning Traces
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Watchlist */}
          <Card className="border-t-4 border-amber-500 bg-amber-50/50 rounded-xl shadow-sm">
            <CardHeader
              title={
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-amber-600 uppercase">
                    Watchlist
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {watchlist.length} items
                  </span>
                </div>
              }
            />
            <CardContent className="space-y-3">
                            {watchlist.length === 0 && !isLoading && (
                <p className="text-xs text-slate-400">
                  No items on the watchlist.
                </p>
              )}
              {watchlist.map((alert) => (
                <div
                  key={alert.id}
                  className="rounded-lg border border-amber-400 bg-white px-3 py-2 shadow-sm"
                >
                  <p className="text-sm font-semibold text-slate-900">
                    {alert.title}
                  </p>
                  <p className="text-xs text-slate-600">
                    Impact: Medium ({alert.impactedPoCount} POs affected)
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Status: Monitoring · Decision Pending
                  </p>
                  <div className="flex gap-2 mt-2">
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleViewDetails(alert)}
                      sx={{ textTransform: 'none', fontSize: '11px' }}
                    >
                      View Details
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleReasoningTraces(alert)}
                      sx={{ textTransform: 'none', fontSize: '11px' }}
                    >
                      Reasoning Traces
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Safe Zone */}
          <Card className="border-t-4 border-green-500 bg-green-50/50 rounded-xl shadow-sm">
            <CardHeader
              title={
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-green-600 uppercase">
                    Safe Zone
                  </span>
                  <span className="text-[10px] text-slate-400">
                    99% On-Track
                  </span>
                </div>
              }
            />
            <CardContent className="space-y-3">
              {safe.length === 0 && !isLoading && (
                <p className="text-xs text-slate-400">
                  No suppliers in the Safe Zone based on current filters.
                </p>
              )}
              {safe.map((alert) => (
                <div
                  key={alert.id}
                  className="rounded-lg border border-green-400 bg-white px-3 py-2 shadow-sm"
                >
                  <p className="text-sm font-semibold text-slate-900">
                    {alert.location?.label ?? 'Supplier'}
                  </p>
                  <p className="text-xs text-slate-600">
                    Status: Normal · Performance: 99% On-Track
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {alert.title}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Modal for View Details */}
        <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: 500,
              bgcolor: 'background.paper',
              boxShadow: 24,
              p: 4,
              borderRadius: 2,
            }}
          >
            <h2 className="text-xl font-bold mb-4">Alert Details</h2>
            {selectedAlertForModal && (
              <div className="space-y-2 text-sm">
                <p>
                  <strong>Title:</strong> {selectedAlertForModal.title}
                </p>
                <p>
                  <strong>Severity:</strong> {selectedAlertForModal.severity}
                </p>
                <p>
                  <strong>Source:</strong> {selectedAlertForModal.source}
                </p>
                <p>
                  <strong>Time Detected:</strong>{' '}
                  {new Date(selectedAlertForModal.detectedAt).toLocaleString()}
                </p>
                <p>
                  <strong>Description:</strong> {selectedAlertForModal.description}
                </p>
                <p>
                  <strong>Impacted POs:</strong> {selectedAlertForModal.impactedPoCount}
                </p>
              </div>
            )}
            <div className="mt-6 flex gap-2">
              <Button variant="outlined" onClick={() => setModalOpen(false)}>
                Close
              </Button>
              {selectedAlertForModal && (
                <Button
                  variant="contained"
                  onClick={() => {
                    setModalOpen(false);
                    handleAnalyzeImpact(selectedAlertForModal);
                  }}
                  sx={{
                    bgcolor: '#E57373',
                    '&:hover': { bgcolor: '#D84315' },
                  }}
                >
                  Analyze Financial Impact
                </Button>
              )}
            </div>
          </Box>
        </Modal>

        {/* Drawer for Reasoning Traces */}
        <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
          <Box sx={{ width: 450, p: 3 }}>
            <h2 className="text-xl font-bold mb-4">Reasoning Traces</h2>
            {selectedAlertForModal && (
              <div className="space-y-4 text-sm">
                <div>
                  <strong className="block mb-1">Alert:</strong>
                  <p className="text-slate-600">{selectedAlertForModal.title}</p>
                </div>
                <div>
                  <strong className="block mb-1">AI Reasoning:</strong>
                  <p className="text-slate-600">
                    This alert was triggered because the monitoring signals indicated a
                    potential risk based on historical data and current thresholds.
                  </p>
                </div>
                <div>
                  <strong className="block mb-1">Chain of Thought:</strong>
                  <ol className="list-decimal list-inside space-y-1 text-slate-600">
                    <li>Detected anomaly in logistics data</li>
                    <li>Cross-referenced with weather and geopolitical factors</li>
                    <li>Calculated impact exceeding threshold (${(selectedAlertForModal.estimatedRevenueImpact / 1000).toFixed(0)}k)</li>
                    <li>Triggered alert with severity: {selectedAlertForModal.severity}</li>
                  </ol>
                </div>
                <div>
                  <strong className="block mb-1">Confidence Score:</strong>
                  <p className="text-slate-600">87% - High confidence based on multiple signals</p>
                </div>
              </div>
            )}
            <Button
              variant="outlined"
              fullWidth
              onClick={() => setDrawerOpen(false)}
              sx={{ mt: 4 }}
            >
              Close
            </Button>
          </Box>
        </Drawer>
      </div>
    </div>
  );
}

