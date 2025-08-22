import React, { useState, useEffect } from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Alert,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    IconButton,
    Tooltip
} from '@mui/material';
import {
    Refresh as RefreshIcon,
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, Legend } from 'recharts';

interface SystemMetrics {
    cpuUsage: number;
    memoryUsage: {
        total: number;
        used: number;
        free: number;
        percentUsed: number;
    };
    diskUsage: {
        total: number;
        used: number;
        free: number;
        percentUsed: number;
    };
    networkConnections: number;
    uptime: number;
}

interface DetectedMiner {
    ip: string;
    mac: string;
    hostname: string;
    confidence: number;
    detectedAt: string;
    status: 'active' | 'blocked' | 'warning';
    ports: number[];
    miningPools: string[];
}

const Dashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
    const [miners, setMiners] = useState<DetectedMiner[]>([]);
    const [alerts, setAlerts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [historicalData, setHistoricalData] = useState<any[]>([]);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [metricsResponse, minersResponse, alertsResponse] = await Promise.all([
                fetch('/api/stats'),
                fetch('/api/miners'),
                fetch('/api/alerts')
            ]);

            const [metricsData, minersData, alertsData] = await Promise.all([
                metricsResponse.json(),
                minersResponse.json(),
                alertsResponse.json()
            ]);

            setMetrics(metricsData);
            setMiners(minersData);
            setAlerts(alertsData);

            // Update historical data
            setHistoricalData(prev => [...prev, {
                timestamp: new Date().toISOString(),
                cpuUsage: metricsData.cpuUsage,
                memoryUsage: metricsData.memoryUsage.percentUsed,
                minerCount: minersData.length
            }].slice(-20)); // Keep last 20 data points

        } catch (err) {
            setError('Failed to fetch dashboard data');
            console.error('Dashboard fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleBlockMiner = async (ip: string) => {
        try {
            await fetch(`/api/miners/${ip}/block`, { method: 'POST' });
            await fetchData(); // Refresh data
        } catch (err) {
            setError('Failed to block miner');
            console.error('Block miner error:', err);
        }
    };

    if (loading && !metrics) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" onClose={() => setError(null)}>
                {error}
            </Alert>
        );
    }

    return (
        <Box p={3}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4">System Dashboard</Typography>
                <Button
                    startIcon={<RefreshIcon />}
                    onClick={fetchData}
                    variant="contained"
                >
                    Refresh
                </Button>
            </Box>

            {/* System Metrics Cards */}
            <Grid container spacing={3} mb={3}>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                CPU Usage
                            </Typography>
                            <Typography variant="h5">
                                {metrics?.cpuUsage.toFixed(1)}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Memory Usage
                            </Typography>
                            <Typography variant="h5">
                                {metrics?.memoryUsage.percentUsed.toFixed(1)}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Disk Usage
                            </Typography>
                            <Typography variant="h5">
                                {metrics?.diskUsage.percentUsed.toFixed(1)}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Active Connections
                            </Typography>
                            <Typography variant="h5">
                                {metrics?.networkConnections}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Historical Data Chart */}
            <Card mb={3}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        System Performance History
                    </Typography>
                    <LineChart width={1200} height={300} data={historicalData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <ChartTooltip />
                        <Legend />
                        <Line type="monotone" dataKey="cpuUsage" stroke="#8884d8" name="CPU Usage (%)" />
                        <Line type="monotone" dataKey="memoryUsage" stroke="#82ca9d" name="Memory Usage (%)" />
                        <Line type="monotone" dataKey="minerCount" stroke="#ff7300" name="Detected Miners" />
                    </LineChart>
                </CardContent>
            </Card>

            {/* Detected Miners Table */}
            <Card mb={3}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Detected Miners
                    </Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Status</TableCell>
                                    <TableCell>IP Address</TableCell>
                                    <TableCell>Hostname</TableCell>
                                    <TableCell>Confidence</TableCell>
                                    <TableCell>Detected At</TableCell>
                                    <TableCell>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {miners.map((miner) => (
                                    <TableRow key={miner.ip}>
                                        <TableCell>
                                            {miner.status === 'active' && (
                                                <Tooltip title="Active Mining">
                                                    <WarningIcon color="error" />
                                                </Tooltip>
                                            )}
                                            {miner.status === 'blocked' && (
                                                <Tooltip title="Blocked">
                                                    <CheckCircleIcon color="success" />
                                                </Tooltip>
                                            )}
                                            {miner.status === 'warning' && (
                                                <Tooltip title="Suspicious Activity">
                                                    <ErrorIcon color="warning" />
                                                </Tooltip>
                                            )}
                                        </TableCell>
                                        <TableCell>{miner.ip}</TableCell>
                                        <TableCell>{miner.hostname}</TableCell>
                                        <TableCell>{(miner.confidence * 100).toFixed(1)}%</TableCell>
                                        <TableCell>{new Date(miner.detectedAt).toLocaleString()}</TableCell>
                                        <TableCell>
                                            <Button
                                                variant="contained"
                                                color="secondary"
                                                size="small"
                                                onClick={() => handleBlockMiner(miner.ip)}
                                                disabled={miner.status === 'blocked'}
                                            >
                                                {miner.status === 'blocked' ? 'Blocked' : 'Block'}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </CardContent>
            </Card>

            {/* Recent Alerts */}
            <Card>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Recent Alerts
                    </Typography>
                    {alerts.map((alert, index) => (
                        <Alert
                            key={index}
                            severity={alert.severity}
                            sx={{ mb: 1 }}
                        >
                            {alert.message}
                        </Alert>
                    ))}
                </CardContent>
            </Card>
        </Box>
    );
};

export default Dashboard;