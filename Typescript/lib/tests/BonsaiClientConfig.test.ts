/*
 * BonsaiClientConfig.test.ts
 *
 * Tests for the Config Class.
 */

import { BonsaiClientConfig } from '../src/simulator/client/bonsaiClientConfig';

describe('environmental variables', () => {
    const OLD_ENV = process.env;

    beforeEach(() => {
        jest.resetModules();
        process.env = { ...OLD_ENV };
    });

    afterAll(() => {
        process.env = OLD_ENV;
    });

    test('Config defaults', async () => {
        process.env.SIM_API_HOST = undefined;
        process.env.SIM_WORKSPACE = undefined;
        process.env.SIM_ACCESS_KEY = undefined;
        process.env.SIM_CONTEXT = undefined;

        const config = new BonsaiClientConfig();
        expect(config.server).toBe('https://api.bons.ai');
        expect(config.workspace).toBe('');
        expect(config.accessKey).toBe('');
        expect(config.simulatorContext).toContain('simulatorClientId');
    });

    test('Config constructor', async () => {
        process.env.SIM_API_HOST = undefined;
        process.env.SIM_WORKSPACE = undefined;
        process.env.SIM_ACCESS_KEY = undefined;
        process.env.SIM_CONTEXT = undefined;

        const config = new BonsaiClientConfig('foo', 'bar');
        expect(config.server).toBe('https://api.bons.ai');
        expect(config.workspace).toBe('foo');
        expect(config.accessKey).toBe('bar');
        expect(config.simulatorContext).toContain('simulatorClientId');
    });

    test('Config with env variables', () => {
        process.env.SIM_API_HOST = 'https://my-api.com';
        process.env.SIM_WORKSPACE = 'foo';
        process.env.SIM_ACCESS_KEY = 'bar';
        process.env.SIM_CONTEXT = 'fizz';

        const config = new BonsaiClientConfig();
        expect(config.server).toBe('https://my-api.com');
        expect(config.workspace).toBe('foo');
        expect(config.accessKey).toBe('bar');
        expect(config.simulatorContext).toBe('fizz');
    });
});

describe('command line args', () => {
    const OLD_ARGS = process.argv;

    beforeEach(() => {
        jest.resetModules();
        process.argv = OLD_ARGS;
    });

    afterAll(() => {
        process.argv = OLD_ARGS;
    });

    test('Config with env variables', () => {
        process.argv = ['node', 'thisScript', '--accesskey=111', '--workspace=workspaces', '--sim-context=bar'];

        const config = new BonsaiClientConfig();
        expect(config.server).toBe('https://api.bons.ai');
        expect(config.workspace).toBe('workspaces');
        expect(config.accessKey).toBe('111');
        expect(config.simulatorContext).toBe('bar');
    });
});
