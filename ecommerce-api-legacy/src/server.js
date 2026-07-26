const config = require('./config');
const createApp = require('./app');

async function start() {
    const { app, db } = await createApp();
    const server = app.listen(config.port, () => {
        console.log('Frankenstein LMS rodando na porta ' + config.port + '...');
    });

    let shuttingDown = false;
    const shutdown = () => {
        if (shuttingDown) return;
        shuttingDown = true;
        server.close(async () => {
            try {
                await db.close();
                process.exit(0);
            } catch (error) {
                console.error(error);
                process.exit(1);
            }
        });
    };

    process.once('SIGINT', shutdown);
    process.once('SIGTERM', shutdown);
}

start().catch(error => {
    console.error(error);
    process.exit(1);
});
